import json
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from redis import Redis
from redis.exceptions import RedisError

from . import models, schemas
from .config import settings
from .database import engine, get_db

models.ChargingRecord.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title="EV-Charging-System Charging Service")
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

# --- 业务接口：注意字段映射 ---
# 修改为正确的类名 ChargingRecordOut 和 ChargingRecordCreate
@app.post("/charging", response_model=schemas.ChargingRecordOut)
def create_charging_record(
    record: schemas.ChargingRecordCreate, 
    db: Session = Depends(get_db), 
    username: str = Depends(get_current_user),
):
    station = get_station_for_update(record.station_id, db)
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
