from sqlalchemy.orm import Session

from app.models import Measurement
from app.schemas import TelemetryIn


def evaluate_status(data: TelemetryIn) -> tuple[str, str | None]:
    critical = []
    warning = []

    if data.temperature_c >= 90:
        critical.append("temperatura crítica")
    elif data.temperature_c >= 75:
        warning.append("temperatura elevada")

    if data.vibration_mm_s >= 7.1:
        critical.append("vibração crítica")
    elif data.vibration_mm_s >= 4.5:
        warning.append("vibração elevada")

    if data.current_a >= 18:
        critical.append("sobrecorrente crítica")
    elif data.current_a >= 14:
        warning.append("corrente elevada")

    if data.rpm < 1200:
        critical.append("rotação criticamente baixa")
    elif data.rpm < 1500:
        warning.append("rotação baixa")

    if critical:
        return "critical", "; ".join(critical)
    if warning:
        return "warning", "; ".join(warning)
    return "normal", None


def save_measurement(db: Session, data: TelemetryIn) -> Measurement:
    status, alarm = evaluate_status(data)
    row = Measurement(
        machine_id=data.machine_id,
        temperature_c=data.temperature_c,
        vibration_mm_s=data.vibration_mm_s,
        current_a=data.current_a,
        rpm=data.rpm,
        status=status,
        alarm_message=alarm,
        recorded_at=data.timestamp,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
