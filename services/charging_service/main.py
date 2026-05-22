from fastapi import FastAPI, Depends, HTTPException, status
import requests
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from . import models, schemas
from .config import settings
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EV-Charging-System Charging Service")

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

def notify_station_charging(station_id: int, token: str):
    try:
        response = requests.put(
            f"{settings.STATION_SERVICE_URL}/stations/{station_id}/status",
            json={"status": "充电中"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Station status update failed: {exc}",
        )

# --- 业务接口：注意字段映射 ---
# 修改为正确的类名 ChargingRecordOut 和 ChargingRecordCreate
@app.post("/charging", response_model=schemas.ChargingRecordOut)
def create_charging_record(
    record: schemas.ChargingRecordCreate, 
    db: Session = Depends(get_db), 
    username: str = Depends(get_current_user),
    token: str = Depends(settings.oauth2_scheme)
):
    notify_station_charging(record.station_id, token)

    new_record = models.ChargingRecord(
        user_id=username,
        station_id=record.station_id,   
        kwh_consumed=record.kwh_consumed, 
        duration_minutes=record.duration_minutes
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record
