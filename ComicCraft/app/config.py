from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.8-flash"
    hf_api_key: str = ""
    image_model: str = "black-forest-labs/FLUX.1-schnell"
    image_provider: str = "huggingface"
    use_local_diffusers: bool = False
    output_dir: str = str(BASE_DIR / "static")
    max_prompt_length: int = 2000
    request_timeout_seconds: int = 180
    gemini_fallback_models: str = "gemini-3.7-flash,gemini-3.6-flash"
    gemini_max_retries: int = 3
    gemini_retry_base_seconds: float = 3.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
