from fastapi import FastAPI

from layer_ai.api.routes import register_routes
from layer_ai.config import Settings
from layer_ai.services.jobs import JobService
from layer_ai.text import build_text_extractor
from layer_ai.text.base import TextExtractor
from layer_ai.visual import build_visual_extractor
from layer_ai.visual.base import VisualExtractor


def create_app(
    settings: Settings | None = None,
    text_extractor: TextExtractor | None = None,
    visual_extractor: VisualExtractor | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings()
    app = FastAPI(title="Layer AI API", version="0.1.0")
    app.state.settings = resolved_settings
    app.state.job_service = JobService(
        resolved_settings,
        text_extractor=text_extractor or build_text_extractor(resolved_settings),
        visual_extractor=visual_extractor or build_visual_extractor(resolved_settings),
    )
    register_routes(app)
    return app
