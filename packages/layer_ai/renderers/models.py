from pydantic import BaseModel, Field

from layer_ai.contracts.models import BoundingBox, EditableText


class RendererLayerRef(BaseModel):
    id: str
    name: str
    type: str
    z_index: int
    bbox: BoundingBox
    cropped_asset_path: str
    full_canvas_asset_path: str
    mask_asset_path: str
    confidence: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    text_content: str | None = None
    text_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    editable_text: EditableText | None = None


class RendererHandoff(BaseModel):
    job_id: str
    renderer: str
    created_at: str
    manifest_path: str
    original_image_path: str
    background_asset_path: str
    global_confidence: float = Field(ge=0.0, le=1.0)
    reconstruction_score: float | None = Field(default=None, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    layers: list[RendererLayerRef] = Field(default_factory=list)


class RendererHandoffResult(BaseModel):
    job_id: str
    renderer: str
    handoff_path: str
    layer_count: int = Field(ge=0)
