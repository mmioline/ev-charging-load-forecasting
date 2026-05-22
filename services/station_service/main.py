from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import List
from jose import JWTError, jwt

from . import models, schemas
from .config import settings
from .database import engine, get_db
from .realtime_status import cache_station_status, get_cached_station_status

# 自动建表
models.Base.metadata.create_all(bind=engine)

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

def build_station_response(station: models.Station) -> dict:
    cached_status = get_cached_station_status(station.id)
    if cached_status:
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
    if cached_status:
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
    stations = db.query(models.Station).all()
    return [build_station_response(station) for station in stations]

@app.get("/stations/status/available", response_model=List[schemas.StationOut])
def list_available_stations(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
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
    return build_station_response(station)

@app.get("/stations/{station_id}/status", response_model=schemas.StationStatusOut)
def get_station_status(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    station = get_station_or_404(station_id, db)
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
