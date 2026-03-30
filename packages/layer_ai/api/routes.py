from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from layer_ai.errors import InvalidImageError
from layer_ai.renderers import RendererNotImplementedError, get_renderer_adapter

ALLOWED_IMAGE_MEDIA_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}


def register_routes(app: FastAPI) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": app.state.settings.service_name}

    @app.post("/v1/jobs", status_code=status.HTTP_201_CREATED)
    async def create_job(
        image: UploadFile = File(...),
        instruction: str = Form(..., min_length=1),
    ) -> dict:
        if image.content_type not in ALLOWED_IMAGE_MEDIA_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported image media type",
            )

        try:
            job_record = await app.state.job_service.create_job(
                image_bytes=await image.read(),
                filename=image.filename or "input.png",
                instruction=instruction,
            )
        except InvalidImageError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file",
            ) from error
        return {
            "job_id": job_record.job_id,
            "status": job_record.status.value,
            "route": job_record.route,
            "global_confidence": job_record.global_confidence,
        }

    @app.get("/v1/jobs/{job_id}")
    def get_job(job_id: str) -> dict:
        job_record = app.state.job_service.get_job(job_id)
        if job_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        return {
            "job_id": job_record.job_id,
            "status": job_record.status.value,
            "route": job_record.route,
            "global_confidence": job_record.global_confidence,
            "created_at": job_record.created_at,
        }

    @app.get("/v1/jobs/{job_id}/manifest")
    def get_manifest(job_id: str) -> dict:
        manifest = app.state.job_service.get_manifest(job_id)
        if manifest is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return manifest

    @app.get("/v1/jobs/{job_id}/assets")
    def get_assets(job_id: str) -> FileResponse:
        asset_path = app.state.job_service.get_assets_archive(job_id)
        if asset_path is None or not Path(asset_path).exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assets not found")
        return FileResponse(
            path=asset_path,
            media_type="application/zip",
            filename=f"{job_id}.zip",
        )

    @app.post("/v1/jobs/{job_id}/render/after-effects")
    def render_after_effects(job_id: str) -> dict:
        return _render_job(app, job_id, "after-effects")

    @app.post("/v1/jobs/{job_id}/render/remotion")
    def render_remotion(job_id: str) -> dict:
        return _render_job(app, job_id, "remotion")


def _render_job(app: FastAPI, job_id: str, renderer_name: str) -> dict:
    manifest = app.state.job_service.get_manifest(job_id)
    if manifest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    adapter = get_renderer_adapter(renderer_name)
    try:
        return adapter.handoff(job_id, manifest)
    except RendererNotImplementedError as error:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(error)) from error
