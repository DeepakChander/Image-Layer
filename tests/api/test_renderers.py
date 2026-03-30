from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from layer_ai.api.app import create_app
from layer_ai.config import Settings


def _sample_png_bytes() -> bytes:
    image = Image.new("RGB", (120, 80), color=(10, 20, 30))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_renderer_handoff_returns_not_implemented_for_existing_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))
    create_response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract and render"},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(f"/v1/jobs/{job_id}/render/after-effects")

    assert response.status_code == 501
    assert response.json()["detail"] == "Renderer adapter not implemented"


def test_renderer_handoff_returns_404_for_unknown_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.post("/v1/jobs/job_missing/render/remotion")

    assert response.status_code == 404
