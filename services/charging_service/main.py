import json
import time
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from redis import Redis
from redis.exceptions import RedisError

from . import models, schemas
from .config import settings
from .database import engine, get_db

def wait_for_database(retries: int = 20, delay_seconds: float = 1.5) -> None:
    for attempt in range(1, retries + 1):
        try:
            models.ChargingRecord.__table__.create(bind=engine, checkfirst=True)
            return
        except SQLAlchemyError:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)


wait_for_database()


def ensure_charging_runtime_columns():
    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns("charging_records")}

    with engine.begin() as connection:
        if "kwh_consumed" in existing_columns and engine.dialect.name == "mysql":
            connection.execute(
                text("ALTER TABLE charging_records MODIFY COLUMN kwh_consumed FLOAT NOT NULL")
            )


ensure_charging_runtime_columns()

app = FastAPI(title="EV-Charging-System Charging Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_current_user(token: str = Depends(settings.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

def cache_station_status(station_id: int, status_value: str, last_updated_at: datetime) -> None:
    payload = {
        "station_id": station_id,
        "status": status_value,
        "last_updated_at": last_updated_at.isoformat(),
    }
    try:
        redis_client.set(f"station:status:{station_id}", json.dumps(payload, ensure_ascii=False))
    except RedisError:
        pass


def get_station_for_update(station_id: int, db: Session) -> models.Station:
    station = (
        db.query(models.Station)
        .filter(models.Station.id == station_id)
        .with_for_update()
        .first()
    )
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


# 可接受充电的站点状态白名单
CHARGEABLE_STATUS = {"空闲"}


@app.post("/charging", response_model=schemas.ChargingRecordOut)
def create_charging_record(
    record: schemas.ChargingRecordCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
):
    station = get_station_for_update(record.station_id, db)

    # 状态校验：非空闲站点拒绝充电请求
    if station.status not in CHARGEABLE_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"站点当前状态为「{station.status}」，无法发起充电",
        )

    now = datetime.utcnow()
    new_record = models.ChargingRecord(
        user_id=username,
        station_id=record.station_id,
        kwh_consumed=record.kwh_consumed,
        duration_minutes=record.duration_minutes
    )
    db.add(new_record)
    station.status = "充电中"
    station.last_updated_at = now
    db.commit()
    db.refresh(new_record)
    db.refresh(station)
    cache_station_status(station.id, station.status, station.last_updated_at)
    return new_record


@app.get("/charging", response_model=List[schemas.ChargingRecordOut])
def list_my_charging_records(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
):
    return (
        db.query(models.ChargingRecord)
        .filter(models.ChargingRecord.user_id == username)
        .order_by(models.ChargingRecord.created_at.desc())
        .all()
    )


@app.get("/charging/{record_id}", response_model=schemas.ChargingRecordOut)
def get_my_charging_record(
    record_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
):
    record = (
        db.query(models.ChargingRecord)
        .filter(
            models.ChargingRecord.id == record_id,
            models.ChargingRecord.user_id == username,
        )
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Charging record not found")
    return record