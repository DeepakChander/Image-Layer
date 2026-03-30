def build_example_manifest() -> dict:
    return {
        "package_version": "1.0.0",
        "schema_version": "1.0.0",
        "job_id": "job_example_001",
        "route": "design_route",
        "status": "completed_high_confidence",
        "global_confidence": 1.0,
        "warnings": [],
        "canvas": {
            "width": 160,
            "height": 90,
        },
        "layers": [
            {
                "id": "layer_001_background",
                "name": "background",
                "type": "background",
                "bbox": {"x": 0, "y": 0, "width": 160, "height": 90},
                "z_index": 0,
                "parent_id": None,
                "cropped_asset": "layers/cropped/layer_001_background.png",
                "full_canvas_asset": "layers/full_canvas/layer_001_background.png",
                "mask_asset": "layers/masks/layer_001_background_mask.png",
                "confidence": 1.0,
                "warnings": [],
                "editable_text": None,
            }
        ],
    }


def build_example_scene_graph() -> dict:
    return {
        "job_id": "job_example_001",
        "root_id": "scene_root",
        "nodes": [
            {
                "id": "scene_root",
                "type": "group",
                "name": "scene",
                "children": ["layer_001_background"],
                "z_index": 0,
            },
            {
                "id": "layer_001_background",
                "type": "background",
                "name": "background",
                "children": [],
                "z_index": 0,
            },
        ],
    }


def build_scene_graph(job_id: str, layers: list[dict]) -> dict:
    return {
        "job_id": job_id,
        "root_id": "scene_root",
        "nodes": [
            {
                "id": "scene_root",
                "type": "group",
                "name": "scene",
                "children": [layer["id"] for layer in sorted(layers, key=lambda layer: layer["z_index"])],
                "z_index": 0,
            },
            *[
                {
                    "id": layer["id"],
                    "type": layer["type"],
                    "name": layer["name"],
                    "children": [],
                    "z_index": layer["z_index"],
                }
                for layer in sorted(layers, key=lambda layer: layer["z_index"])
            ],
        ],
    }
