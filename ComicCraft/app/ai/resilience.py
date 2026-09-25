import asyncio
from app.config import get_settings

def is_transient_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(x in text for x in ("503", "unavailable", "service unavailable", "429", "resource_exhausted", "rate limit", "500", "internal server error", "502", "504", "deadline"))

def model_candidates(primary: str) -> list[str]:
    settings = get_settings()
    return list(dict.fromkeys([primary] + [x.strip() for x in settings.gemini_fallback_models.split(",") if x.strip()]))

async def generate_with_resilience(client, prompt: str, primary_model: str, config):
    settings = get_settings(); candidates = model_candidates(primary_model); last_error=None
    for model in candidates:
        for attempt in range(settings.gemini_max_retries):
            try:
                return await client.aio.models.generate_content(model=model, contents=prompt, config=config)
            except Exception as exc:
                last_error=exc
                if not is_transient_error(exc): raise
                if attempt < settings.gemini_max_retries-1:
                    await asyncio.sleep(settings.gemini_retry_base_seconds * (2 ** attempt))
    raise RuntimeError("Gemini is temporarily unavailable after retries. Tried models: " + ", ".join(candidates) + ". Please wait and try again.") from last_error
