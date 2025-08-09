# Dirt to Meme Magic

Turn any image into a meme in seconds. This repo contains a FastAPI backend and a React + Vite + TailwindCSS frontend.

## Project Structure

- backend/ → FastAPI app (meme generation)
- src/ → React + Vite app (UI in `src/pages/Index.tsx`)

## Prerequisites

- Python 3.10+
- Node.js 18+

## 1) Run the Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will:
- Accept image uploads at POST http://127.0.0.1:8000/upload
- Detect faces (OpenCV) to pick a suitable caption set
- Render meme text using Pillow (Anton font) and add a small decorative overlay from `backend/templates/`
- Return JSON with a downloadable meme URL under `/static/...`

## 2) Run the Frontend (React + Vite)

```bash
# From project root
npm i
npm run dev
```

Open http://localhost:5173 to use the app. The frontend calls the backend at http://127.0.0.1:8000 by default (configurable in `src/config.ts`).

## How It Works

1. Drop or select any image in the UI.
2. The frontend uploads it to the FastAPI `/upload` endpoint.
3. The backend analyzes for faces (if found → face captions; else → general captions).
4. It draws an all-caps meme caption with a black outline, optionally adds a small overlay (from `backend/templates/`), and returns a URL to the generated image.

## Notes

- CORS is enabled for local development.
- Six small, embedded template images live in `backend/templates/`.
- If OpenCV isn’t available, the app still works (falls back to non-face captions).

## Troubleshooting

- If fonts fail to load, ensure `backend/assets/Anton-Regular.ttf` exists and restart the backend.
- If uploads fail, confirm the backend is running on 127.0.0.1:8000 and your browser can reach it.

## License

This project is for demo/educational purposes. Template images are generated assets included in this repository.
