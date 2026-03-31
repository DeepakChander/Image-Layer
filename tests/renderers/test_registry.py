from layer_ai.renderers.models import RendererHandoff, RendererHandoffResult


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
