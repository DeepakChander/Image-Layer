import json

from layer_ai.renderers.after_effects import AfterEffectsRendererAdapter


def _touch(path):  # noqa: ANN001,ANN202
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"stub")


def test_after_effects_adapter_writes_renderer_handoff_json(tmp_path):
    job_root = tmp_path / "job_000001"
    _touch(job_root / "input" / "original.png")
    _touch(job_root / "layers" / "cropped" / "layer_001_background.png")
    _touch(job_root / "layers" / "full_canvas" / "layer_001_background.png")
    _touch(job_root / "layers" / "masks" / "layer_001_background_mask.png")
    _touch(job_root / "layers" / "cropped" / "layer_002_text_001.png")
    _touch(job_root / "layers" / "full_canvas" / "layer_002_text_001.png")
    _touch(job_root / "layers" / "masks" / "layer_002_text_001_mask.png")

    manifest = {
        "job_id": "job_000001",
        "global_confidence": 0.94,
        "reconstruction_score": 0.99,
        "warnings": ["possible_duplicate_layers"],
        "layers": [
            {
                "id": "layer_001_background",
                "name": "background",
                "type": "background",
                "bbox": {"x": 0, "y": 0, "width": 240, "height": 120},
                "z_index": 0,
                "cropped_asset": "layers/cropped/layer_001_background.png",
                "full_canvas_asset": "layers/full_canvas/layer_001_background.png",
                "mask_asset": "layers/masks/layer_001_background_mask.png",
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
                "bbox": {"x": 24, "y": 20, "width": 32, "height": 10},
                "z_index": 1,
                "cropped_asset": "layers/cropped/layer_002_text_001.png",
                "full_canvas_asset": "layers/full_canvas/layer_002_text_001.png",
                "mask_asset": "layers/masks/layer_002_text_001_mask.png",
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

    result = AfterEffectsRendererAdapter().handoff(
        job_id="job_000001",
        job_root=job_root,
        manifest=manifest,
    )

    handoff_path = job_root / "renderers" / "after-effects" / "renderer_handoff.json"
    payload = json.loads(handoff_path.read_text(encoding="utf-8"))

    assert result.handoff_path == "renderers/after-effects/renderer_handoff.json"
    assert payload["background_asset_path"] == str(job_root / "layers" / "full_canvas" / "layer_001_background.png")
    assert [layer["id"] for layer in payload["layers"]] == ["layer_001_background", "layer_002_text_001"]
    assert payload["layers"][1]["text_content"] == "HELLO"
    assert payload["layers"][1]["editable_text"]["text"] == "HELLO"
