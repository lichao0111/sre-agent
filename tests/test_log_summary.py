from fastapi.testclient import TestClient
from sre_agent.app.main import app


client = TestClient(app)


def test_log_summary_and_diagnosis():
    payload = {"source": "monitor", "raw": "service:auth|error: database timeout request_id=abc-123"}
    r = client.post("/webhook/event", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert "log_summary" in data["structured"]
    assert data["structured"]["service_name"] == "auth"
    assert data["diagnosis"]["diagnosis"] == "DB_TIMEOUT"
    assert data["diagnosis"]["log_summary"] == data["structured"]["log_summary"]
