import time
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from jose import JWTError, jwt

from . import models, schemas
from .config import settings
from .database import engine, get_db
from .realtime_status import cache_station_status, get_cached_station_status

# 自动建表
def wait_for_database(retries: int = 20, delay_seconds: float = 1.5) -> None:
    for attempt in range(1, retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            return
        except SQLAlchemyError:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)


wait_for_database()

def ensure_station_runtime_columns():
    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns("stations")}

    with engine.begin() as connection:
        if "status" not in existing_columns:
            connection.execute(
                text("ALTER TABLE stations ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT '空闲'")
            )

        if "last_updated_at" not in existing_columns:
            if engine.dialect.name == "mysql":
                connection.execute(
                    text(
                        "ALTER TABLE stations "
                        "ADD COLUMN last_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
                    )
                )
            else:
                connection.execute(text("ALTER TABLE stations ADD COLUMN last_updated_at DATETIME"))

ensure_station_runtime_columns()

app = FastAPI(title="EV-Charging-System Station Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(token: str = Depends(settings.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

def get_station_or_404(station_id: int, db: Session) -> models.Station:
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


def parse_cached_datetime(value: str):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None

STALE_CHARGING_THRESHOLD = timedelta(hours=24)


def mark_stale_charging_stations(db: Session) -> None:
    stale_before = datetime.utcnow() - STALE_CHARGING_THRESHOLD
    stale_stations = (
        db.query(models.Station)
        .filter(
            models.Station.status == schemas.StationStatus.charging.value,
            models.Station.last_updated_at < stale_before,
        )
        .all()
    )
    if not stale_stations:
        return

    now = datetime.utcnow()
    for station in stale_stations:
        station.status = schemas.StationStatus.abnormal.value
        station.last_updated_at = now

    db.commit()
    for station in stale_stations:
        db.refresh(station)
        cache_station_status(station.id, station.status, station.last_updated_at)


def refresh_stale_station_status(station: models.Station, db: Session) -> models.Station:
    stale_before = datetime.utcnow() - STALE_CHARGING_THRESHOLD
    if (
        station.status == schemas.StationStatus.charging.value
        and station.last_updated_at
        and station.last_updated_at < stale_before
    ):
        station.status = schemas.StationStatus.abnormal.value
        station.last_updated_at = datetime.utcnow()
        db.commit()
        db.refresh(station)
        cache_station_status(station.id, station.status, station.last_updated_at)
    return station


def build_station_response(station: models.Station) -> dict:
    cached_status = get_cached_station_status(station.id)
    cached_updated_at = parse_cached_datetime(cached_status.get("last_updated_at")) if cached_status else None
    if (
        cached_status
        and cached_updated_at
        and station.last_updated_at
        and cached_updated_at >= station.last_updated_at
    ):
        return {
            "id": station.id,
            "name": station.name,
            "location": station.location,
            "capacity": station.capacity,
            "slots": station.slots,
            "status": cached_status["status"],
            "last_updated_at": cached_status["last_updated_at"],
        }

    return {
        "id": station.id,
        "name": station.name,
        "location": station.location,
        "capacity": station.capacity,
        "slots": station.slots,
        "status": station.status,
        "last_updated_at": station.last_updated_at,
    }

def build_status_response(station: models.Station) -> dict:
    cached_status = get_cached_station_status(station.id)
    cached_updated_at = parse_cached_datetime(cached_status.get("last_updated_at")) if cached_status else None
    if (
        cached_status
        and cached_updated_at
        and station.last_updated_at
        and cached_updated_at >= station.last_updated_at
    ):
        return {
            "station_id": station.id,
            "status": cached_status["status"],
            "last_updated_at": cached_status["last_updated_at"],
        }

    cache_station_status(station.id, station.status, station.last_updated_at)
    return {
        "station_id": station.id,
        "status": station.status,
        "last_updated_at": station.last_updated_at,
    }

# --- 业务接口：注意这里的 StationCreate 和 StationOut ---
@app.post("/stations", response_model=schemas.StationOut) 
def create_station(
    station: schemas.StationCreate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    new_station = models.Station(**station.model_dump()) 
    db.add(new_station)
    db.commit()
    db.refresh(new_station)
    cache_station_status(new_station.id, new_station.status, new_station.last_updated_at)
    return build_station_response(new_station)

@app.get("/stations", response_model=List[schemas.StationOut])
def list_stations(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    mark_stale_charging_stations(db)
    stations = db.query(models.Station).all()
    return [build_station_response(station) for station in stations]

@app.get("/stations/status/available", response_model=List[schemas.StationOut])
def list_available_stations(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    mark_stale_charging_stations(db)
    stations = db.query(models.Station).all()
    station_responses = [build_station_response(station) for station in stations]
    return [
        station
        for station in station_responses
        if station["status"] == schemas.StationStatus.available.value
    ]

@app.get("/stations/{station_id}", response_model=schemas.StationOut)
def get_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    station = get_station_or_404(station_id, db)
    station = refresh_stale_station_status(station, db)
    return build_station_response(station)

@app.get("/stations/{station_id}/status", response_model=schemas.StationStatusOut)
def get_station_status(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    station = get_station_or_404(station_id, db)
    station = refresh_stale_station_status(station, db)
    return build_status_response(station)

@app.put("/stations/{station_id}/status", response_model=schemas.StationStatusOut)
def update_station_status(
    station_id: int,
    status_update: schemas.StationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    station = get_station_or_404(station_id, db)
    now = datetime.utcnow()

    station.status = status_update.status.value
    station.last_updated_at = now
    db.commit()
    db.refresh(station)

    cache_station_status(station.id, station.status, station.last_updated_at)
    return build_status_response(station)
