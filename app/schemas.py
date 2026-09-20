from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class TelemetryIn(BaseModel):
    machine_id: str = Field(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    temperature_c: float = Field(ge=-50, le=250)
    vibration_mm_s: float = Field(ge=0, le=100)
    current_a: float = Field(ge=0, le=500)
    rpm: float = Field(ge=0, le=10000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MeasurementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: str
    temperature_c: float
    vibration_mm_s: float
    current_a: float
    rpm: float
    status: str
    alarm_message: str | None
    recorded_at: datetime
