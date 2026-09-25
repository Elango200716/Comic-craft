import json
from app.config import get_settings
from app.schemas import PromptRequest
from app.ai.resilience import generate_with_resilience

async def generate_story(request: PromptRequest, outline: list[dict]) -> list[dict]:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Expand this comic outline into concise panel narration and dialogue.

Character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}

Outline:
{json.dumps(outline, ensure_ascii=False, indent=2)}

Return ONLY a JSON array of exactly 5 objects with:
panel_number, caption, narration, dialogue.
Dialogue should be short and natural.
"""
    response = await generate_with_resilience(
        client, prompt, settings.gemini_story_model,
        types.GenerateContentConfig(response_mime_type="application/json"),
    )
    data = json.loads(response.text or "[]")
    if len(data) != 5:
        raise ValueError("Gemini returned an incorrect number of story panels.")
    return data
