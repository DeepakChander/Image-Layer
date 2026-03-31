import json
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from layer_ai.api.app import create_app
from layer_ai.config import Settings
from layer_ai.renderers.after_effects import AfterEffectsRendererAdapter
from layer_ai.renderers.base import UnsupportedRendererError
from layer_ai.renderers.models import RendererHandoff, RendererHandoffResult
from layer_ai.renderers.registry import get_renderer_adapter
from layer_ai.renderers.remotion import RemotionRendererAdapter


def test_renderer_handoff_models_capture_job_and_layer_metadata():
    handoff = RendererHandoff.model_validate(
        {
            "job_id": "job_000001",
            "renderer": "after-effects",
            "created_at": "2026-03-31T00:00:00Z",
            "manifest_path": "manifest/manifest.json",
            "original_image_path": "input/original.png",
            "background_asset_path": "layers/full_canvas/layer_001_background.png",
            "global_confidence": 0.92,
            "reconstruction_score": 0.98,
            "warnings": ["possible_duplicate_layers"],
            "layers": [
                {
                    "id": "layer_001_background",
                    "name": "background",
                    "type": "background",
                    "z_index": 0,
                    "bbox": {"x": 0, "y": 0, "width": 240, "height": 120},
                    "cropped_asset_path": "layers/cropped/layer_001_background.png",
                    "full_canvas_asset_path": "layers/full_canvas/layer_001_background.png",
                    "mask_asset_path": "layers/masks/layer_001_background_mask.png",
                    "confidence": 1.0,
                    "warnings": [],
                    "text_content": None,
                    "text_confidence": None,
                    "editable_text": None,
                },
                {
                    "id": "layer_002_text_001",
                    "name": "hello text",
                    "type": "text",
                    "z_index": 1,
                    "bbox": {"x": 24, "y": 20, "width": 32, "height": 10},
                    "cropped_asset_path": "layers/cropped/layer_002_text_001.png",
                    "full_canvas_asset_path": "layers/full_canvas/layer_002_text_001.png",
                    "mask_asset_path": "layers/masks/layer_002_text_001_mask.png",
                    "confidence": 0.99,
                    "warnings": [],
                    "text_content": "HELLO",
                    "text_confidence": 0.99,
                    "editable_text": {
                        "text": "HELLO",
                        "font_family_guess": "Unknown",
                        "font_weight": 400,
                        "font_size_px": 10,
                        "fill": "#000000",
                        "alignment": "left",
                        "confidence": 0.99,
                    },
                },
            ],
        }
    )

    result = RendererHandoffResult.model_validate(
        {
            "job_id": "job_000001",
            "renderer": "after-effects",
            "handoff_path": "renderers/after-effects/renderer_handoff.json",
            "layer_count": 2,
        }
    )

    assert [layer.id for layer in handoff.layers] == ["layer_001_background", "layer_002_text_001"]
    assert handoff.layers[1].editable_text.text == "HELLO"
    assert result.handoff_path == "renderers/after-effects/renderer_handoff.json"


def test_registry_returns_real_renderer_adapters():
    assert isinstance(get_renderer_adapter("after-effects"), AfterEffectsRendererAdapter)
    assert isinstance(get_renderer_adapter("remotion"), RemotionRendererAdapter)


def test_registry_rejects_unknown_renderer_names():
    with pytest.raises(UnsupportedRendererError):
        get_renderer_adapter("not-a-renderer")


def _sample_png_bytes() -> bytes:
    image = Image.new("RGB", (120, 80), color=(10, 20, 30))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_renderer_cli_generates_handoff_for_existing_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")
    client = TestClient(create_app(settings))
    create_response = client.post(
        "/v1/jobs",
        files={"image": ("sample.png", _sample_png_bytes(), "image/png")},
        data={"instruction": "Extract and render"},
    )
    job_id = create_response.json()["job_id"]

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[2] / "apps" / "worker" / "run_renderer.py"),
            "--job-id",
            job_id,
            "--renderer",
            "after-effects",
            "--storage-root",
            str(settings.storage_root),
        ],
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["renderer"] == "after-effects"
    assert payload["handoff_path"] == "renderers/after-effects/renderer_handoff.json"


def test_renderer_cli_returns_non_zero_for_missing_job(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts", ocr_backend="disabled")

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[2] / "apps" / "worker" / "run_renderer.py"),
            "--job-id",
            "job_missing",
            "--renderer",
            "after-effects",
            "--storage-root",
            str(settings.storage_root),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Job not found" in result.stderr
