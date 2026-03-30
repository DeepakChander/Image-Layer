from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from PIL import Image

from layer_ai.api.app import create_app
from layer_ai.config import Settings
from layer_ai.contracts.registry import load_contract_schema


def _sample_png_bytes() -> bytes:
    image = Image.new("RGB", (160, 90), color=(32, 64, 128))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_create_job_generates_manifest_and_package(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "completed_high_confidence"
    assert body["job_id"].startswith("job_")

    status_response = client.get(f"/v1/jobs/{body['job_id']}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed_high_confidence"

    manifest_response = client.get(f"/v1/jobs/{body['job_id']}/manifest")
    assert manifest_response.status_code == 200
    manifest = manifest_response.json()
    assert manifest["job_id"] == body["job_id"]
    assert manifest["layers"][0]["type"] == "background"
    assert manifest["layers"][0]["cropped_asset"].endswith(".png")
    validator = Draft202012Validator(load_contract_schema("manifest"))
    assert list(validator.iter_errors(manifest)) == []

    assets_response = client.get(f"/v1/jobs/{body['job_id']}/assets")
    assert assets_response.status_code == 200
    assert assets_response.headers["content-type"] == "application/zip"

    with ZipFile(BytesIO(assets_response.content)) as archive:
        names = set(archive.namelist())

    assert "input/original.png" in names
    assert "input/normalized.png" in names
    assert "manifest/manifest.json" in names
    assert "manifest/scene_graph.json" in names
    assert "layers/cropped/layer_001_background.png" in names
    assert "layers/full_canvas/layer_001_background.png" in names
    assert "layers/masks/layer_001_background_mask.png" in names
    assert "preview/reconstructed.png" in names
    assert "job.json" not in names
    assert "manifest-pointer.json" not in names


def test_create_job_requires_instruction(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
    )

    assert response.status_code == 422


def test_get_unknown_job_returns_404(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.get("/v1/jobs/job_missing")

    assert response.status_code == 404


def test_create_job_rejects_unsupported_media_type(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.txt", b"not-an-image", "text/plain")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported image media type"


def test_create_job_rejects_invalid_image_bytes(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", b"not-a-real-png", "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file"
