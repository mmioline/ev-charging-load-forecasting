from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List

from . import models, schemas, database
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

# --- 业务接口：注意字段映射 ---
# 修改为正确的类名 ChargingRecordOut 和 ChargingRecordCreate
@app.post("/charging", response_model=schemas.ChargingRecordOut)
def create_charging_record(
    record: schemas.ChargingRecordCreate, 
    db: Session = Depends(get_db), 
    username: str = Depends(get_current_user)
):
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