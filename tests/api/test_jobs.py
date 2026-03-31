from io import BytesIO
import json
from zipfile import ZipFile

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from PIL import Image, ImageDraw, ImageFont

from layer_ai.api.app import create_app
from layer_ai.config import Settings
from layer_ai.contracts.registry import load_contract_schema
from layer_ai.text.models import TextCandidate
from layer_ai.visual.models import VisualCandidate


def _sample_png_bytes() -> bytes:
    image = Image.new("RGB", (160, 90), color=(32, 64, 128))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _text_png_bytes(text: str = "HELLO") -> bytes:
    image = Image.new("RGB", (240, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((24, 36), text, fill=(0, 0, 0), font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _visual_png_bytes() -> bytes:
    image = Image.new("RGB", (240, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((32, 28, 108, 72), fill=(27, 99, 198), radius=8)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class StubTextExtractor:
    def __init__(self, candidates: list[TextCandidate]) -> None:
        self._candidates = candidates

    def extract(self, image_path, image):  # noqa: ANN001
        return self._candidates


class ExplodingTextExtractor:
    def extract(self, image_path, image):  # noqa: ANN001
        raise RuntimeError("OCR backend crashed")


class StubVisualExtractor:
    def __init__(self, candidates: list[VisualCandidate]) -> None:
        self._candidates = candidates

    def extract(self, image, text_candidates):  # noqa: ANN001
        return self._candidates


def test_create_job_generates_manifest_and_package(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
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
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
    )

    assert response.status_code == 422


def test_get_unknown_job_returns_404(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.get("/v1/jobs/job_missing")

    assert response.status_code == 404


def test_create_job_rejects_unsupported_media_type(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.txt", b"not-an-image", "text/plain")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported image media type"


def test_create_job_rejects_invalid_image_bytes(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", b"not-a-real-png", "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file"


def test_create_job_rejects_empty_image_payload(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("empty.png", b"", "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Image file is empty"


def test_create_job_marks_job_as_failed_when_text_extractor_crashes(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(
        create_app(settings, text_extractor=ExplodingTextExtractor()),
        raise_server_exceptions=False,
    )

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 500
    job_record = client.app.state.job_service.get_job("job_000001")
    assert job_record is not None
    assert job_record.status == "failed_processing_error"


def test_create_job_exports_raster_text_layers_when_ocr_finds_text(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    text_extractor = StubTextExtractor(
        [
            TextCandidate(
                text="HELLO",
                confidence=0.95,
                bbox={"x": 24, "y": 36, "width": 40, "height": 10},
                polygon=[(24, 36), (64, 36), (64, 46), (24, 46)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=text_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("text.png", _text_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 201
    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()
    assert len(manifest["layers"]) == 2
    text_layer = next(layer for layer in manifest["layers"] if layer["type"] == "text")
    assert text_layer["text_content"] == "HELLO"
    assert text_layer["text_confidence"] == 0.95
    assert text_layer["editable_text"] is None

    assets_response = client.get(f"/v1/jobs/{response.json()['job_id']}/assets")
    with ZipFile(BytesIO(assets_response.content)) as archive:
        names = set(archive.namelist())
        assert "layers/cropped/layer_002_text_001.png" in names
        assert "layers/full_canvas/layer_002_text_001.png" in names
        assert "layers/masks/layer_002_text_001_mask.png" in names


def test_create_job_emits_editable_text_when_confidence_is_high(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    text_extractor = StubTextExtractor(
        [
            TextCandidate(
                text="PRICING",
                confidence=0.995,
                bbox={"x": 30, "y": 40, "width": 55, "height": 12},
                polygon=[(30, 40), (85, 40), (85, 52), (30, 52)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=text_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("text.png", _text_png_bytes("PRICING"), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()
    text_layer = next(layer for layer in manifest["layers"] if layer["type"] == "text")
    assert text_layer["editable_text"]["text"] == "PRICING"
    assert text_layer["editable_text"]["confidence"] == 0.995


def test_create_job_scene_graph_matches_detected_layers(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    text_extractor = StubTextExtractor(
        [
            TextCandidate(
                text="CONTACT",
                confidence=0.96,
                bbox={"x": 40, "y": 42, "width": 60, "height": 12},
                polygon=[(40, 42), (100, 42), (100, 54), (40, 54)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=text_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("text.png", _text_png_bytes("CONTACT"), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assets_response = client.get(f"/v1/jobs/{response.json()['job_id']}/assets")
    with ZipFile(BytesIO(assets_response.content)) as archive:
        scene_graph = json.loads(archive.read("manifest/scene_graph.json"))

    node_ids = {node["id"] for node in scene_graph["nodes"]}
    assert "scene_root" in node_ids
    assert "layer_001_background" in node_ids
    assert "layer_002_text_001" in node_ids

    scene_root = next(node for node in scene_graph["nodes"] if node["id"] == "scene_root")
    assert "layer_001_background" in scene_root["children"]
    assert "layer_002_text_001" in scene_root["children"]


def test_create_job_background_layer_removes_detected_text_region(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    text_extractor = StubTextExtractor(
        [
            TextCandidate(
                text="HELLO",
                confidence=0.95,
                bbox={"x": 24, "y": 36, "width": 40, "height": 10},
                polygon=[(24, 36), (64, 36), (64, 46), (24, 46)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=text_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("text.png", _text_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assets_response = client.get(f"/v1/jobs/{response.json()['job_id']}/assets")
    with ZipFile(BytesIO(assets_response.content)) as archive:
        original = Image.open(BytesIO(archive.read("input/original.png"))).convert("RGBA")
        background = Image.open(BytesIO(archive.read("layers/full_canvas/layer_001_background.png"))).convert(
            "RGBA"
        )

    original_crop = original.crop((24, 36, 64, 46))
    background_crop = background.crop((24, 36, 64, 46))
    assert original_crop.tobytes() != background_crop.tobytes()


def test_create_job_downgrades_status_and_confidence_for_low_confidence_text(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    text_extractor = StubTextExtractor(
        [
            TextCandidate(
                text="HELLO",
                confidence=0.55,
                bbox={"x": 24, "y": 36, "width": 40, "height": 10},
                polygon=[(24, 36), (64, 36), (64, 46), (24, 46)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=text_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("text.png", _text_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "completed_low_confidence"
    assert response.json()["global_confidence"] == 0.55

    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()
    assert manifest["status"] == "completed_low_confidence"
    assert manifest["global_confidence"] == 0.55
    assert "low_text_confidence" in manifest["warnings"]


def test_create_job_exports_visual_layers_when_visual_extractor_finds_components(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    visual_extractor = StubVisualExtractor(
        [
            VisualCandidate(
                label="cta_button",
                layer_type="button",
                confidence=0.84,
                bbox={"x": 32, "y": 28, "width": 76, "height": 44},
                mask=[[255] * 76 for _ in range(44)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=StubTextExtractor([]), visual_extractor=visual_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("visual.png", _visual_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    assert response.status_code == 201
    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()
    visual_layer = next(layer for layer in manifest["layers"] if layer["type"] == "button")
    assert visual_layer["bbox"] == {"x": 32, "y": 28, "width": 76, "height": 44}
    assert visual_layer["confidence"] == 0.84

    assets_response = client.get(f"/v1/jobs/{response.json()['job_id']}/assets")
    with ZipFile(BytesIO(assets_response.content)) as archive:
        names = set(archive.namelist())
    assert "layers/cropped/layer_002_button_001.png" in names
    assert "layers/full_canvas/layer_002_button_001.png" in names
    assert "layers/masks/layer_002_button_001_mask.png" in names


def test_create_job_exposes_reconstruction_metrics_in_manifest_and_logs(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))

    response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()
    assert manifest["reconstruction_score"] == 1.0
    assert manifest["preview_diff_ratio"] == 0.0

    assets_response = client.get(f"/v1/jobs/{response.json()['job_id']}/assets")
    with ZipFile(BytesIO(assets_response.content)) as archive:
        confidence_report = json.loads(archive.read("logs/confidence_report.json"))

    assert confidence_report["reconstruction_score"] == 1.0
    assert confidence_report["preview_diff_ratio"] == 0.0


def test_create_job_fuses_duplicate_visual_layers_and_warns(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    visual_extractor = StubVisualExtractor(
        [
            VisualCandidate(
                label="cta_button",
                layer_type="button",
                confidence=0.84,
                bbox={"x": 32, "y": 28, "width": 76, "height": 44},
                mask=[[255] * 76 for _ in range(44)],
            ),
            VisualCandidate(
                label="cta_button_duplicate",
                layer_type="button",
                confidence=0.9,
                bbox={"x": 34, "y": 30, "width": 76, "height": 44},
                mask=[[255] * 76 for _ in range(44)],
            ),
        ]
    )
    client = TestClient(create_app(settings, text_extractor=StubTextExtractor([]), visual_extractor=visual_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("visual.png", _visual_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()
    button_layers = [layer for layer in manifest["layers"] if layer["type"] == "button"]

    assert len(button_layers) == 1
    assert "possible_duplicate_layers" in manifest["warnings"]


def test_create_job_warns_when_reconstruction_score_is_poor(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    visual_extractor = StubVisualExtractor(
        [
            VisualCandidate(
                label="cta_button_wrong_region",
                layer_type="button",
                confidence=0.84,
                bbox={"x": 90, "y": 10, "width": 40, "height": 20},
                mask=[[255] * 40 for _ in range(20)],
            )
        ]
    )
    client = TestClient(create_app(settings, text_extractor=StubTextExtractor([]), visual_extractor=visual_extractor))

    response = client.post(
        "/v1/jobs",
        files={"image": ("visual.png", _visual_png_bytes(), "image/png")},
        data={"instruction": "Extract layers and prepare motion-ready assets"},
    )

    manifest = client.get(f"/v1/jobs/{response.json()['job_id']}/manifest").json()

    assert manifest["reconstruction_score"] < 0.9
    assert "reconstruction_mismatch" in manifest["warnings"]
    assert manifest["status"] in {"completed_with_warnings", "completed_low_confidence"}
