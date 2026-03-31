from layer_ai.fusion.engine import FusionEngine


def _layer(
    layer_id: str,
    layer_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z_index: int,
    confidence: float = 0.9,
):
    return {
        "id": layer_id,
        "name": layer_id,
        "type": layer_type,
        "bbox": {"x": x, "y": y, "width": width, "height": height},
        "z_index": z_index,
        "confidence": confidence,
        "warnings": [],
    }


def test_fusion_prefers_text_over_overlapping_visual():
    engine = FusionEngine()
    text_layer = _layer("layer_text", "text", 10, 10, 50, 20, z_index=1)
    visual_layer = _layer("layer_button", "button", 12, 10, 50, 20, z_index=2)

    fused = engine.fuse(text_layers=[text_layer], visual_layers=[visual_layer])

    assert [layer["id"] for layer in fused.layers] == ["layer_text"]
    assert fused.warnings == []


def test_fusion_collapses_near_duplicate_visual_layers_and_warns():
    engine = FusionEngine()
    first = _layer("layer_button_a", "button", 20, 30, 80, 40, z_index=3, confidence=0.82)
    second = _layer("layer_button_b", "button", 22, 32, 80, 40, z_index=4, confidence=0.88)

    fused = engine.fuse(text_layers=[], visual_layers=[first, second])

    assert [layer["id"] for layer in fused.layers] == ["layer_button_b"]
    assert fused.warnings == ["possible_duplicate_layers"]


def test_fusion_preserves_deterministic_ordering_by_z_index_then_id():
    engine = FusionEngine()
    text_layer = _layer("layer_text", "text", 10, 10, 40, 10, z_index=4)
    first_visual = _layer("layer_shape_b", "shape", 80, 10, 30, 30, z_index=2)
    second_visual = _layer("layer_shape_a", "shape", 120, 10, 30, 30, z_index=2)

    fused = engine.fuse(text_layers=[text_layer], visual_layers=[first_visual, second_visual])

    assert [layer["id"] for layer in fused.layers] == [
        "layer_shape_a",
        "layer_shape_b",
        "layer_text",
    ]
