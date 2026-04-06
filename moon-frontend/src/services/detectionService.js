import { API_BASE } from "./api"

export async function detectImage(file) {
  const form = new FormData()
  form.append("file", file)

  const res = await fetch(`${API_BASE}/detect`, {
    method: "POST",
    body: form
  })

  if (!res.ok) throw new Error("Detection failed")
  return res.json()
}

export async function getDetections(uploadId) {
  const res = await fetch(`${API_BASE}/detections/${uploadId}`)
  if (!res.ok) throw new Error("Fetch failed")
  return res.json()
}
