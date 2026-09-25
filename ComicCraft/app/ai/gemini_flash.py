import json
import re
from typing import Any
from app.config import get_settings
from app.schemas import PromptRequest
from app.ai.resilience import generate_with_resilience

def _extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < start:
        raise ValueError("Gemini did not return a JSON array.")
    return json.loads(text[start:end + 1])

async def generate_outline(request: PromptRequest) -> list[dict]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Create a cohesive 5-panel comic outline.

User story: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Return ONLY a JSON array of exactly 5 objects. Each object must contain:
panel_number (1-5), title, scene_description, image_prompt.
The image_prompt must describe composition, character appearance, action, setting,
lighting, camera framing, and visual style. Do not include text, speech bubbles,
logos, watermarks, or captions inside the image. Keep the main character consistent.
"""
    response = await generate_with_resilience(
        client, prompt, settings.gemini_model,
        types.GenerateContentConfig(response_mime_type="application/json"),
    )
    data = _extract_json(response.text or "")
    if len(data) != 5:
        raise ValueError("Gemini returned an outline with an incorrect panel count.")
    for i, panel in enumerate(data, 1):
        panel["panel_number"] = i
    return data
