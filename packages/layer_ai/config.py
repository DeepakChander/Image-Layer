from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "layer-ai-api"
    storage_root: Path = Field(default=Path("artifacts"))

    model_config = SettingsConfigDict(
        env_prefix="LAYER_AI_",
        env_file=".env",
        extra="ignore",
    )

