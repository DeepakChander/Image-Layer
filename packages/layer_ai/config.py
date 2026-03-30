from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "layer-ai-api"
    storage_root: Path = Field(default=Path("artifacts"))
    ocr_backend: str = "auto"
    editable_text_confidence_threshold: float = Field(default=0.99, ge=0.0, le=1.0)

    model_config = SettingsConfigDict(
        env_prefix="LAYER_AI_",
        env_file=".env",
        extra="ignore",
    )
