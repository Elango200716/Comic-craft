from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.ai.image_generator import generate_image
from app.exporters import save_pdf
from app.layout_builder import build_comic_layout
from app.schemas import PromptRequest

async def create_comic(request: PromptRequest) -> dict:
    outline = await generate_outline(request)
    story = await generate_story(request, outline)

    panels = []
    for outline_panel, story_panel in zip(outline, story):
        image_path = await generate_image(
            outline_panel["image_prompt"],
            outline_panel["panel_number"],
        )
        panels.append({
            **outline_panel,
            **story_panel,
            "image_path": image_path,
        })

    layout = build_comic_layout(panels)
    pdf_url = save_pdf(layout, title=f"ComicCraft - {request.character_name}")
    return {
        "title": f"ComicCraft - {request.character_name}",
        "panels": layout,
        "pdf_url": pdf_url,
    }
