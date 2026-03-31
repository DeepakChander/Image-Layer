from jsonschema import Draft202012Validator

from layer_ai.contracts.examples import build_example_manifest, build_example_scene_graph
from layer_ai.contracts.registry import load_contract_schema


def test_example_manifest_matches_manifest_schema():
    schema = load_contract_schema("manifest")
    validator = Draft202012Validator(schema)

    example_manifest = build_example_manifest()
    assert example_manifest["reconstruction_score"] == 1.0
    assert example_manifest["preview_diff_ratio"] == 0.0

    errors = sorted(validator.iter_errors(example_manifest), key=lambda item: item.path)

    assert errors == []


def test_example_scene_graph_matches_scene_graph_schema():
    schema = load_contract_schema("scene_graph")
    validator = Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(build_example_scene_graph()), key=lambda item: item.path)

    assert errors == []
