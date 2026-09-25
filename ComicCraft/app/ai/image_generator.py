import asyncio
from pathlib import Path
from uuid import uuid4

from PIL import Image
from app.config import get_settings


async def generate_image(image_prompt: str, panel_number: int) -> str:
    settings = get_settings()
    output_dir = Path(settings.output_dir) / "panels"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"panel_{panel_number}_{uuid4().hex[:8]}.png"
    destination = output_dir / filename

    if settings.use_local_diffusers:
        return await _generate_local(image_prompt, destination)

    if settings.image_provider.lower() != "huggingface":
        raise RuntimeError("Unsupported IMAGE_PROVIDER. Use 'huggingface' or local Diffusers.")

    if not settings.hf_api_key:
        raise RuntimeError("HF_API_KEY is not configured.")

    # Current Hugging Face Inference Providers route image generation through
    # the official InferenceClient instead of the retired/legacy
    # api-inference.huggingface.co endpoint. provider='auto' can route to an
    # available provider and fail over when the preferred provider is unavailable.
    from huggingface_hub import InferenceClient

    def run():
        client = InferenceClient(
            api_key=settings.hf_api_key,
            provider="auto",
            timeout=settings.request_timeout_seconds,
        )
        image = client.text_to_image(
            prompt=image_prompt,
            model=settings.image_model,
        )
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        image.convert("RGB").save(destination, format="PNG")

    try:
        await asyncio.to_thread(run)
    except Exception as exc:
        raise RuntimeError(
            "Hugging Face image generation failed. "
            "Check HF_API_KEY, Hugging Face Inference Provider access/credits, "
            "and your internet connection. "
            f"Details: {exc}"
        ) from exc

    return f"/static/panels/{filename}"


async def _generate_local(prompt: str, destination: Path) -> str:
    def run():
        import torch
        from diffusers import StableDiffusionPipeline
        pipe = StableDiffusionPipeline.from_pretrained(
            get_settings().image_model,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = pipe.to(device)
        image = pipe(prompt, num_inference_steps=25, guidance_scale=7.0).images[0]
        image.save(destination, format="PNG")
    await asyncio.to_thread(run)
    return f"/static/panels/{destination.name}"
