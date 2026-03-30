from enum import StrEnum

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    EXPORTING_ASSETS = "exporting_assets"
    COMPLETED_HIGH_CONFIDENCE = "completed_high_confidence"
    FAILED_PROCESSING_ERROR = "failed_processing_error"


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class EditableText(BaseModel):
    text: str
    font_family_guess: str
    font_weight: int
    font_size_px: int
    fill: str
    alignment: str
    confidence: float = Field(ge=0.0, le=1.0)


class LayerEntry(BaseModel):
    id: str
    name: str
    type: str
    bbox: BoundingBox
    z_index: int
    parent_id: str | None = None
    cropped_asset: str
    full_canvas_asset: str
    mask_asset: str
    confidence: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    editable_text: EditableText | None = None


class Canvas(BaseModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class SceneManifest(BaseModel):
    package_version: str
    schema_version: str
    job_id: str
    route: str
    status: str
    global_confidence: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    canvas: Canvas
    layers: list[LayerEntry]


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    route: str
    global_confidence: float | None = None
    instruction: str
    created_at: str
    artifact_zip_path: str | None = None

