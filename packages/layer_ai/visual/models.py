from pydantic import BaseModel, Field

from layer_ai.contracts.models import BoundingBox


class VisualCandidate(BaseModel):
    label: str
    layer_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox
    mask: list[list[int]]
    warnings: list[str] = Field(default_factory=list)
