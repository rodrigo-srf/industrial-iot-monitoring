from datetime import datetime, timezone

from app.schemas import TelemetryIn
from app.services import evaluate_status


def telemetry(**changes):
    values = {
        "machine_id": "MOTOR-01",
        "temperature_c": 65,
        "vibration_mm_s": 2.1,
        "current_a": 10,
        "rpm": 1750,
        "timestamp": datetime.now(timezone.utc),
    }
    values.update(changes)
    return TelemetryIn(**values)


def test_normal_operation():
    assert evaluate_status(telemetry()) == ("normal", None)


def test_warning_operation():
    status, message = evaluate_status(telemetry(temperature_c=78, vibration_mm_s=5))
    assert status == "warning"
    assert "temperatura elevada" in message
    assert "vibração elevada" in message


def test_critical_has_priority():
    status, message = evaluate_status(telemetry(temperature_c=95, current_a=15))
    assert status == "critical"
    assert message == "temperatura crítica"
