from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routes import router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "panels").mkdir(exist_ok=True)
(STATIC_DIR / "exports").mkdir(exist_ok=True)

app = FastAPI(
    title="ComicCraft",
    description="AI comic story creator using Gemini and Stable Diffusion-compatible image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)
