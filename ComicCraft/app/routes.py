from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.schemas import PromptRequest
from app.services import create_comic
from app.ai.image_generator import generate_image

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = await create_comic(PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        ))
        return templates.TemplateResponse(request=request, name="comic_preview.html", context=data)
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )

@router.post("/generate-comic/json")
async def generate_json(payload: PromptRequest):
    try:
        return await create_comic(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_url: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_url": pdf_url},
    )

@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        path = await generate_image(prompt, 0)
        return {"image_url": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
