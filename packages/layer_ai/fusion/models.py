from pydantic import BaseModel, Field


class FusionResult(BaseModel):
    layers: list[dict]
    warnings: list[str] = Field(default_factory=list)
