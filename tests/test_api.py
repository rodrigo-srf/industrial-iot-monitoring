from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_create_and_list_measurement():
    with TestClient(app) as client:
        payload = {
            "machine_id": "MOTOR-01",
            "temperature_c": 80,
            "vibration_mm_s": 2.5,
            "current_a": 11,
            "rpm": 1740,
            "timestamp": "2026-09-20T12:00:00Z",
        }
        response = client.post("/api/measurements", json=payload)
        assert response.status_code == 201
        assert response.json()["status"] == "warning"

        machines = client.get("/api/machines")
        assert machines.status_code == 200
        assert machines.json()[0]["machine_id"] == "MOTOR-01"

        alarms = client.get("/api/alarms")
        assert alarms.status_code == 200
        assert len(alarms.json()) == 1


def test_rejects_invalid_machine_id():
    with TestClient(app) as client:
        response = client.post(
            "/api/measurements",
            json={
                "machine_id": "motor 01!",
                "temperature_c": 70,
                "vibration_mm_s": 2,
                "current_a": 10,
                "rpm": 1700,
            },
        )
        assert response.status_code == 422


def test_prometheus_metrics_endpoint():
    with TestClient(app) as client:
        client.get("/api/machines")
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "industrial_http_requests_total" in response.text
        assert "industrial_http_request_duration_seconds" in response.text
