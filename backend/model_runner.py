from __future__ import annotations

from typing import List, Dict, Tuple
from pathlib import Path
from uuid import uuid4
import os

import cv2
import numpy as np
import torch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gradio_client import Client, handle_file

_client: Client | None = None
_midas = None
_midas_transform = None


def _get_client() -> Client:
    global _client
    if _client is None:
        space = os.getenv("SAM3_SPACE", "prithivMLmods/SAM3-Demo")
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            # Support multiple gradio_client versions.
            try:
                _client = Client(space, hf_token=hf_token)
            except TypeError:
                try:
                    _client = Client(space, token=hf_token)
                except TypeError:
                    os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", hf_token)
                    _client = Client(space)
        else:
            _client = Client(space)
    return _client


def _get_midas():
    global _midas, _midas_transform
    if _midas is None:
        _midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        _midas.eval()
        _midas_transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
    return _midas, _midas_transform


def _run_sam3(image_path: str, prompt: str, conf: float):
    client = _get_client()
    result = client.predict(
        source_img=handle_file(image_path),
        text_query=prompt,
        conf_thresh=conf,
        api_name="/run_image_segmentation",
    )
    if os.getenv("SAM3_DEBUG") == "1":
        try:
            def _summarize(obj, depth=0):
                if depth > 2:
                    return type(obj).__name__
                if isinstance(obj, dict):
                    return {k: _summarize(v, depth + 1) for k, v in list(obj.items())[:8]}
                if isinstance(obj, (list, tuple)):
                    return [_summarize(v, depth + 1) for v in list(obj)[:3]]
                return type(obj).__name__

            print(f"[SAM3_DEBUG] prompt={prompt} conf={conf} summary={_summarize(result)}")
        except Exception as exc:
            print(f"[SAM3_DEBUG] summary failed: {exc}")
    return result


def _sam3_result_to_mask(result) -> np.ndarray:
    # Handle dict outputs with annotations containing mask images.
    if isinstance(result, dict):
        annotations = result.get("annotations")
        if isinstance(annotations, list) and annotations:
            masks = []
            for ann in annotations:
                if isinstance(ann, dict):
                    # If annotation includes a mask-like payload, use it.
                    if any(k in ann for k in ("mask", "masks", "segmentation", "data", "value")):
                        try:
                            masks.append(_ensure_mask_array(ann))
                            continue
                        except Exception:
                            pass
                    img_path = ann.get("image")
                    if isinstance(img_path, str) and Path(img_path).exists():
                        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            masks.append(img)
            if masks:
                combined = np.maximum.reduce(masks)
                return combined
        # If no annotations, return empty mask matching the source image size (if available).
        image_path = result.get("image")
        if isinstance(image_path, str) and Path(image_path).exists():
            base = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if base is not None:
                return np.zeros_like(base)
        # Fall back to any mask-like fields at top level.
        try:
            return _ensure_mask_array(result)
        except Exception:
            pass

    # Handle list/tuple outputs where first item is a mask.
    if isinstance(result, (list, tuple)) and len(result) > 0:
        try:
            return _ensure_mask_array(result[0])
        except Exception:
            pass

    # Last resort.
    return _ensure_mask_array(result)


def _ensure_mask_array(mask) -> np.ndarray:
    # Unwrap common Gradio/HF dict/list wrappers to reach the mask array.
    depth = 0
    while True:
        if depth > 6:
            break
        if isinstance(mask, dict):
            if "mask" in mask:
                mask = mask["mask"]
                depth += 1
                continue
            if "masks" in mask and mask["masks"]:
                mask = mask["masks"][0]
                depth += 1
                continue
            if "segmentation" in mask:
                mask = mask["segmentation"]
                depth += 1
                continue
            if "data" in mask:
                mask = mask["data"]
                depth += 1
                continue
            if "value" in mask:
                mask = mask["value"]
                depth += 1
                continue
            # If there's only one value, unwrap it.
            values = list(mask.values())
            if len(values) == 1:
                mask = values[0]
                depth += 1
                continue
            break
        if isinstance(mask, (list, tuple)) and len(mask) == 1:
            mask = mask[0]
            depth += 1
            continue
        break

    # If still a dict/list, try to find the first array-like leaf.
    def _find_array_like(obj, level=0):
        if level > 5:
            return None
        if isinstance(obj, np.ndarray):
            return obj
        if isinstance(obj, (list, tuple)):
            if len(obj) > 0 and isinstance(obj[0], (list, tuple, np.ndarray)):
                return np.array(obj)
            for item in obj:
                found = _find_array_like(item, level + 1)
                if found is not None:
                    return found
        if isinstance(obj, dict):
            for v in obj.values():
                found = _find_array_like(v, level + 1)
                if found is not None:
                    return found
        return None

    if isinstance(mask, (dict, list, tuple)):
        found = _find_array_like(mask)
        if found is not None:
            mask = found

    # If the mask is still a dict, try common file output shapes.
    if isinstance(mask, dict):
        for key in ("path", "file", "name"):
            path_val = mask.get(key)
            if isinstance(path_val, str) and Path(path_val).exists():
                img = cv2.imread(path_val, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    raise ValueError(f"Unable to read mask image from {path_val}.")
                mask = img
                break

    # If mask is a direct file path string.
    if isinstance(mask, str) and Path(mask).exists():
        img = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Unable to read mask image from {mask}.")
        mask = img
    if hasattr(mask, "convert"):
        mask = np.array(mask.convert("L"))
    else:
        mask = np.array(mask)
    if isinstance(mask, np.ndarray) and mask.size == 0:
        raise ValueError("Empty mask received from SAM3 response.")
    if mask.ndim == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    if mask.max() <= 1:
        mask = (mask * 255).astype(np.uint8)
    return mask.astype(np.uint8)


def _mask_to_contours(mask) -> List[np.ndarray]:
    mask_arr = _ensure_mask_array(mask)
    contours, _ = cv2.findContours(mask_arr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def _draw_results(
    image: np.ndarray,
    contours: List[np.ndarray],
    label: str,
    color: Tuple[int, int, int],
) -> Tuple[np.ndarray, List[Dict]]:
    detections: List[Dict] = []
    height, width = image.shape[:2]

    for cnt in contours:
        if cv2.contourArea(cnt) < 200:
            continue

        cv2.drawContours(image, [cnt], -1, color, 2)
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            image,
            label,
            (x, max(0, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

        detections.append(
            {
                "label": label.lower(),
                "confidence": 1.0,
                "x": x / width,
                "y": y / height,
                "width": w / width,
                "height": h / height,
            }
        )

    return image, detections


def _generate_3d(image: np.ndarray, output_path: str):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    midas, transform = _get_midas()

    input_batch = transform(img_rgb)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    midas = midas.to(device)
    input_batch = input_batch.to(device)

    with torch.no_grad():
        prediction = midas(input_batch)

    depth = prediction.squeeze().cpu().numpy()
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)

    h, w = depth.shape
    x_grid, y_grid = np.meshgrid(np.arange(w), np.arange(h))

    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x_grid, y_grid, depth, cmap="viridis", linewidth=0)
    ax.view_init(elev=60, azim=120)
    plt.title("3D Terrain")
    plt.savefig(output_path)
    plt.close(fig)


def _extract_video_frame(video_path: str, output_dir: Path) -> str:
    cap = cv2.VideoCapture(video_path)
    try:
        ok, frame = cap.read()
        if not ok or frame is None:
            raise ValueError("Unable to read a frame from the video.")
    finally:
        cap.release()

    frame_path = output_dir / f"frame_{uuid4().hex}.png"
    cv2.imwrite(str(frame_path), frame)
    return str(frame_path)


def _run_pipeline(image_path: str, output_dir: Path) -> Dict:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read input image.")

    boulder_res = _run_sam3(image_path, "boulder", 0.10)
    crater_res = _run_sam3(image_path, "crater", 0.30)

    boulder_mask = _sam3_result_to_mask(boulder_res)
    crater_mask = _sam3_result_to_mask(crater_res)

    boulder_contours = _mask_to_contours(boulder_mask)
    crater_contours = _mask_to_contours(crater_mask)

    annotated = img.copy()

    annotated, b_detections = _draw_results(
        annotated, boulder_contours, "Boulder", (0, 255, 0)
    )
    annotated, c_detections = _draw_results(
        annotated, crater_contours, "Crater", (255, 0, 0)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = uuid4().hex
    annotated_path = output_dir / f"annotated_{run_id}.png"
    three_d_path = output_dir / f"3d_{run_id}.png"

    cv2.imwrite(str(annotated_path), annotated)
    _generate_3d(annotated, str(three_d_path))

    detections = b_detections + c_detections
    return {
        "annotated": str(annotated_path),
        "3d": str(three_d_path),
        "boulders": len(b_detections),
        "craters": len(c_detections),
        "detections": detections,
    }


def run_inference(file_path: str) -> Dict:
    """
    Runs the SAM3 + MiDaS pipeline.
    Returns:
      {
        "annotated": "...png",
        "3d": "...png",
        "boulders": int,
        "craters": int,
        "detections": [{"label":"crater","confidence":1.0,"x":0.1,"y":0.2,"width":0.3,"height":0.4}]
      }
    """
    output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))
    ext = Path(file_path).suffix.lower()
    if ext in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
        frame_path = _extract_video_frame(file_path, output_dir)
        result = _run_pipeline(frame_path, output_dir)
        result["frame"] = frame_path
        return result

    return _run_pipeline(file_path, output_dir)
