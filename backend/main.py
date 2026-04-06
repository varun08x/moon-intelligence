from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from uuid import uuid4
import psycopg2
from psycopg2.extras import RealDictCursor
from model_runner import run_inference
from dotenv import load_dotenv

app = FastAPI(
    title="Lunar Forge API",
    description="Moon Intelligence backend for uploads and detections.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "docExpansion": "none",
        "displayRequestDuration": True,
        "filter": True,
        "syntaxHighlight.theme": "obsidian"
    }
)

STATIC_DIR = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "db_configured": bool(os.getenv("DATABASE_URL")),
        "sam3_space": os.getenv("SAM3_SPACE", "prithivMLmods/SAM3-Demo"),
    }

def get_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads (
          id BIGSERIAL PRIMARY KEY,
          file_name TEXT NOT NULL,
          file_type TEXT,
          file_path TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cur.execute(
        """
        ALTER TABLE uploads
        ADD COLUMN IF NOT EXISTS file_path TEXT
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS detections (
          id BIGSERIAL PRIMARY KEY,
          upload_id BIGINT NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
          label TEXT,
          confidence DOUBLE PRECISION,
          x DOUBLE PRECISION,
          y DOUBLE PRECISION,
          width DOUBLE PRECISION,
          height DOUBLE PRECISION,
          lat DOUBLE PRECISION,
          lon DOUBLE PRECISION,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Lunar Forge API</title>
        <style>
          :root {
            --bg: #05070d;
            --panel: #0e1324;
            --text: #e7edf7;
            --muted: #a8b3c7;
            --accent: #7dff7a;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: radial-gradient(1200px 600px at 20% -10%, rgba(125,255,122,0.12), transparent 60%),
                        radial-gradient(800px 400px at 80% 10%, rgba(125,255,122,0.08), transparent 60%),
                        var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: grid;
            place-items: center;
          }
          .card {
            width: min(720px, 92vw);
            background: rgba(12, 16, 28, 0.72);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 28px;
            backdrop-filter: blur(10px);
            box-shadow: 0 30px 60px rgba(0,0,0,0.45);
          }
          .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: 2px;
            font-weight: 700;
          }
          .dot {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 12px rgba(125,255,122,0.8);
          }
          h1 {
            margin: 14px 0 6px;
            font-size: 28px;
          }
          p {
            margin: 0 0 18px;
            color: var(--muted);
          }
          .links {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
          }
          a {
            text-decoration: none;
            color: #0b1020;
            background: linear-gradient(90deg, #7dff7a, #b9ff89);
            padding: 10px 14px;
            border-radius: 12px;
            font-weight: 700;
            letter-spacing: 0.6px;
          }
          .pill {
            margin-top: 16px;
            display: inline-flex;
            gap: 8px;
            align-items: center;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(14, 19, 36, 0.7);
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--muted);
            font-size: 12px;
          }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="brand"><img src="/static/logo.svg" alt="Lunar Forge" width="42" height="42" style="display:block"/><span class="dot"></span> LUNAR FORGE</div>
          <h1>Moon Intelligence API</h1>
          <p>Upload imagery, run detections, and stream results to the 3D Moon interface.</p>
          <div class="links">
            <a href="/docs">Open Swagger Docs</a>
            <a href="/redoc">Open ReDoc</a>
            <a href="/admin">Open Admin</a>
          </div>
          <div class="pill">Status: Online ? FastAPI</div>
        </div>
      </body>
    </html>
    """

@app.get("/favicon.ico")
def favicon():
    return FileResponse(STATIC_DIR / "favicon.svg")

@app.get("/stats")
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total_uploads FROM uploads")
    total_uploads = cur.fetchone()["total_uploads"]
    cur.execute("SELECT COUNT(*) AS total_detections FROM detections")
    total_detections = cur.fetchone()["total_detections"]
    cur.close()
    conn.close()
    return {"total_uploads": total_uploads, "total_detections": total_detections}

@app.get("/admin", response_class=HTMLResponse)
def admin():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total_uploads FROM uploads")
    total_uploads = cur.fetchone()["total_uploads"]
    cur.execute("SELECT COUNT(*) AS total_detections FROM detections")
    total_detections = cur.fetchone()["total_detections"]
    cur.execute(
        """
        SELECT id, file_name, file_type, file_path, created_at
        FROM uploads
        ORDER BY created_at DESC
        LIMIT 10
        """
    )
    recent_uploads = cur.fetchall()
    cur.execute(
        """
        SELECT id, upload_id, label, confidence, created_at
        FROM detections
        ORDER BY created_at DESC
        LIMIT 10
        """
    )
    recent_detections = cur.fetchall()
    cur.close()
    conn.close()

    uploads_rows = "".join(
        f"<tr><td>{u['id']}</td><td>{u['file_name']}</td><td>{u['file_type'] or ''}</td><td>{u['file_path'] or ''}</td><td>{u['created_at']}</td></tr>"
        for u in recent_uploads
    )
    detections_rows = "".join(
        f"<tr><td>{d['id']}</td><td>{d['upload_id']}</td><td>{d.get('label','')}</td><td>{d.get('confidence','')}</td><td>{d['created_at']}</td></tr>"
        for d in recent_detections
    )

    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Lunar Forge Admin</title>
        <style>
          :root {{
            --bg: #05070d;
            --panel: #0e1324;
            --text: #e7edf7;
            --muted: #a8b3c7;
            --accent: #7dff7a;
          }}
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: radial-gradient(1200px 600px at 20% -10%, rgba(125,255,122,0.12), transparent 60%),
                        radial-gradient(800px 400px at 80% 10%, rgba(125,255,122,0.08), transparent 60%),
                        var(--bg);
            color: var(--text);
          }}
          header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px 28px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            position: sticky;
            top: 0;
            background: rgba(5,7,13,0.85);
            backdrop-filter: blur(10px);
          }}
          .logo {{ width: 36px; height: 36px; }}
          .title {{ font-weight: 700; letter-spacing: 2px; }}
          .container {{ padding: 24px 28px 48px; display: grid; gap: 18px; }}
          .stats {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); }}
          .card {{ background: rgba(12,16,28,0.75); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 16px; }}
          .label {{ font-size: 12px; letter-spacing: 1.4px; text-transform: uppercase; color: var(--muted); }}
          .value {{ font-size: 24px; font-weight: 700; margin-top: 6px; }}
          table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
          th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
          th {{ color: var(--muted); font-weight: 600; letter-spacing: 0.6px; }}
          .section-title {{ font-weight: 700; margin: 8px 0 10px; }}
        </style>
      </head>
      <body>
        <header>
          <img class="logo" src="/static/logo.svg" alt="Lunar Forge" />
          <div class="title">LUNAR FORGE ADMIN</div>
        </header>
        <div class="container">
          <div class="stats">
            <div class="card"><div class="label">Total Uploads</div><div class="value">{total_uploads}</div></div>
            <div class="card"><div class="label">Total Detections</div><div class="value">{total_detections}</div></div>
          </div>

          <div class="card">
            <div class="section-title">Recent Uploads</div>
            <table>
              <thead><tr><th>ID</th><th>File</th><th>Type</th><th>Path</th><th>Created</th></tr></thead>
              <tbody>{uploads_rows or '<tr><td colspan="5">No uploads yet.</td></tr>'}</tbody>
            </table>
          </div>

          <div class="card">
            <div class="section-title">Recent Detections</div>
            <table>
              <thead><tr><th>ID</th><th>Upload</th><th>Label</th><th>Confidence</th><th>Created</th></tr></thead>
              <tbody>{detections_rows or '<tr><td colspan="5">No detections yet.</td></tr>'}</tbody>
            </table>
          </div>
        </div>
      </body>
    </html>
    """


def save_upload_file(file: UploadFile) -> str:
    suffix = Path(file.filename).suffix if file.filename else ""
    safe_name = f"{uuid4().hex}{suffix}"
    file_path = UPLOAD_DIR / safe_name
    try:
        with file_path.open("wb") as f:
            f.write(file.file.read())
    finally:
        file.file.close()
    return str(file_path)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    file_path = save_upload_file(file)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO uploads (file_name, file_type, file_path)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (file.filename, file.content_type, file_path)
    )
    upload_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return {"upload_id": str(upload_id), "file_path": file_path}

@app.get("/detections/{upload_id}")
def get_detections(upload_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM detections
        WHERE upload_id = %s
        ORDER BY created_at ASC
        """,
        (upload_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"upload_id": upload_id, "detections": rows}

@app.post("/detections/{upload_id}")
def add_detections(upload_id: str, detections: list[dict]):
    conn = get_db()
    cur = conn.cursor()
    for d in detections:
        cur.execute(
            """
            INSERT INTO detections (upload_id, label, confidence, x, y, width, height, lat, lon)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                upload_id,
                d.get("label"),
                d.get("confidence"),
                d.get("x"),
                d.get("y"),
                d.get("width"),
                d.get("height"),
                d.get("lat"),
                d.get("lon"),
            )
        )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "saved", "count": len(detections)}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    file_path = save_upload_file(file)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO uploads (file_name, file_type, file_path)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (file.filename, file.content_type, file_path)
    )
    upload_id = cur.fetchone()["id"]

    result = run_inference(file_path)
    detections = []
    annotated_path = None
    three_d_path = None
    boulders = None
    craters = None
    frame_path = None

    if isinstance(result, dict):
        detections = result.get("detections") or []
        annotated_path = result.get("annotated")
        three_d_path = result.get("3d")
        boulders = result.get("boulders")
        craters = result.get("craters")
        frame_path = result.get("frame")
    elif isinstance(result, list):
        detections = result

    for d in detections:
        cur.execute(
            """
            INSERT INTO detections (upload_id, label, confidence, x, y, width, height, lat, lon)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                upload_id,
                d.get("label"),
                d.get("confidence"),
                d.get("x"),
                d.get("y"),
                d.get("width"),
                d.get("height"),
                d.get("lat"),
                d.get("lon"),
            )
        )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "upload_id": str(upload_id),
        "detections": detections,
        "file_path": file_path,
        "annotated_path": annotated_path,
        "three_d_path": three_d_path,
        "boulders": boulders,
        "craters": craters,
        "frame_path": frame_path,
    }
