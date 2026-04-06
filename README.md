# Lunar Forge: Moon Intelligence
Lunar Forge is a web + ML project that detects lunar surface features (craters, boulders) from imagery and visualizes results in a Three.js UI. It combines a FastAPI backend (SAM3 segmentation + MiDaS depth) with a Vite + React frontend.

## Demo
- Frontend: (add your deployed URL)
- Backend API: (add your deployed URL)

## Demo GIF
Add a short screen recording or GIF here to quickly show the upload -> detection -> output flow.

## Key Features
- Image/video upload and AI inference
- Annotated output with detections
- Depth map visualization
- PostgreSQL metadata storage
- Clean UI with output comparison

## Architecture
```
Frontend (Vite + React + Three.js)
  -> POST /detect (FastAPI)
  -> GET /detections/{id}
  -> GET /outputs/* (annotated, depth)
  -> GET /uploads/* (original)

Backend (FastAPI)
  -> SAM3 via Hugging Face Space
  -> MiDaS depth via Torch Hub
  -> PostgreSQL (uploads + detections)
```

## Tech Stack
- Frontend: React, Vite, Three.js
- Backend: FastAPI, Uvicorn, OpenCV, PyTorch, Matplotlib
- ML: SAM3 (Hugging Face Space), MiDaS
- DB: PostgreSQL

## Local Setup
### Backend
```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd moon-frontend
npm install
npm run dev
```

Create a `moon-frontend/.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Environment Variables (Backend)
See `backend/.env.example` for the full list.
- `DATABASE_URL`
- `HF_TOKEN`
- `SAM3_SPACE`
- `UPLOAD_DIR`
- `OUTPUT_DIR`
- `SAM3_DEBUG`

## Health Check
The backend exposes:
```
GET /health
```

## One-Click Deploy
### Frontend (Vercel)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Backend (Render)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Steps (Recommended)
1. **Render (backend)**
   - Create a new Web Service pointing at the repo
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Add env vars from `backend/.env.example`
2. **Vercel (frontend)**
   - Import repo
   - Root directory: `moon-frontend`
   - Build command: `npm run build`
   - Output: `dist`
   - Env var: `VITE_API_URL` = Render backend URL

## Deployment Notes
- **Frontend**: Vercel (set `VITE_API_URL` to your backend URL)
- **Backend**: Render
  - Add env vars from `.env.example`
  - Ensure a persistent disk or object storage for `/uploads` and `/outputs` if needed

## Project Structure
```
backend/         # FastAPI + ML pipeline
moon-frontend/   # Vite + React UI
```

## Screenshots
Add screenshots here to show the UI + outputs.

## License
MIT
