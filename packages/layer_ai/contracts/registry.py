import json
from pathlib import Path


SCHEMA_DIR = Path(__file__).with_name("schemas")


def load_contract_schema(schema_name: str) -> dict:
    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Unknown schema: {schema_name}")
    return json.loads(schema_path.read_text(encoding="utf-8"))

