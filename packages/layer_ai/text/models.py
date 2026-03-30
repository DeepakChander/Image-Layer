from pydantic import BaseModel, Field

from layer_ai.contracts.models import BoundingBox


class TextCandidate(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox
    polygon: list[tuple[int, int]] = Field(default_factory=list)

