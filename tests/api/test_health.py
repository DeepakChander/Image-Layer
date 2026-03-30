from fastapi.testclient import TestClient

from layer_ai.api.app import create_app
from layer_ai.config import Settings


def test_health_endpoint_reports_ok(tmp_path):
    settings = Settings(storage_root=tmp_path / "artifacts")
    client = TestClient(create_app(settings))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "layer-ai-api"}

