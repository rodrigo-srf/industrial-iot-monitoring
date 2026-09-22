from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, func, select, text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.metrics import install_metrics
from app.models import Measurement
from app.mqtt_client import collector
from app.schemas import MeasurementOut, TelemetryIn
from app.services import save_measurement


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    collector.start()
    yield
    collector.stop()


app = FastAPI(
    title="Monitoramento Industrial com MQTT",
    description="API demonstrativa de telemetria, alarmes e histórico para máquinas industriais.",
    version="1.1.0",
    lifespan=lifespan,
)

install_metrics(app)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "api": "online",
        "database": "online",
        "mqtt": "connected" if collector.connected else "disconnected",
    }


@app.post("/api/measurements", response_model=MeasurementOut, status_code=201)
def create_measurement(data: TelemetryIn, db: Session = Depends(get_db)):
    return save_measurement(db, data)


@app.get("/api/measurements/{machine_id}", response_model=list[MeasurementOut])
def measurement_history(
    machine_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = (
        select(Measurement)
        .where(Measurement.machine_id == machine_id)
        .order_by(desc(Measurement.recorded_at))
        .limit(limit)
    )
    return list(db.scalars(query))


@app.get("/api/machines")
def machines(db: Session = Depends(get_db)):
    latest = (
        select(Measurement.machine_id, func.max(Measurement.id).label("latest_id"))
        .group_by(Measurement.machine_id)
        .subquery()
    )
    query = (
        select(Measurement)
        .join(latest, Measurement.id == latest.c.latest_id)
        .order_by(Measurement.machine_id)
    )
    return [MeasurementOut.model_validate(item) for item in db.scalars(query)]


@app.get("/api/alarms", response_model=list[MeasurementOut])
def alarms(limit: int = Query(default=20, ge=1, le=200), db: Session = Depends(get_db)):
    query = (
        select(Measurement)
        .where(Measurement.status != "normal")
        .order_by(desc(Measurement.recorded_at))
        .limit(limit)
    )
    return list(db.scalars(query))
