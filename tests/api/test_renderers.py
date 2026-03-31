from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from layer_ai.api.app import create_app
from layer_ai.config import Settings
from layer_ai.contracts.models import JobRecord, JobStatus


def _sample_png_bytes() -> bytes:
    image = Image.new("RGB", (120, 80), color=(10, 20, 30))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_renderer_handoff_returns_success_for_completed_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))
    create_response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract and render"},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(f"/v1/jobs/{job_id}/render/after-effects")

    assert response.status_code == 200
    payload = response.json()
    assert payload["renderer"] == "after-effects"
    assert payload["handoff_path"] == "renderers/after-effects/renderer_handoff.json"
    assert (settings.storage_root / job_id / "renderers" / "after-effects" / "renderer_handoff.json").exists()


def test_renderer_handoff_returns_404_for_unknown_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.post("/v1/jobs/job_missing/render/remotion")

    assert response.status_code == 404


def test_renderer_handoff_returns_409_for_incomplete_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    app = create_app(settings)
    app.state.job_service.store.write_job_record(
        JobRecord(
            job_id="job_queued_001",
            status=JobStatus.QUEUED,
            route="design_route",
            global_confidence=None,
            instruction="Extract and render",
            created_at="2026-03-31T00:00:00+00:00",
            artifact_zip_path=None,
        )
    )
    client = TestClient(app)

    response = client.post("/v1/jobs/job_queued_001/render/after-effects")

    assert response.status_code == 409


def test_renderer_handoff_returns_400_for_unknown_renderer_name(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))
    create_response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract and render"},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(f"/v1/jobs/{job_id}/render/not-a-renderer")

    assert response.status_code == 400
