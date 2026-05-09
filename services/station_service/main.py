from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt

from . import models, schemas, database
from .config import settings
from .database import engine, get_db

# 自动建表
models.Base.metadata.create_all(bind=engine)

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
    return new_station

@app.get("/stations", response_model=List[schemas.StationOut])
def list_stations(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return db.query(models.Station).all()