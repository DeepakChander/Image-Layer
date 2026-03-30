from fastapi import FastAPI

from layer_ai.api.routes import register_routes
from layer_ai.config import Settings
from layer_ai.services.jobs import JobService


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    app = FastAPI(title="Layer AI API", version="0.1.0")
    app.state.settings = resolved_settings
    app.state.job_service = JobService(resolved_settings)
    register_routes(app)
    return app

