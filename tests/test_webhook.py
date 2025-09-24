from fastapi.testclient import TestClient
from sre_agent.app.main import app


client = TestClient(app)


def test_receive_event_basic():
    payload = {"source": "monitor", "raw": "service:auth|error: database timeout request_id=abc-123"}
    r = client.post("/webhook/event", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["structured"]["service_name"] == "auth"
    assert data["diagnosis"]["diagnosis"] == "DB_TIMEOUT"
