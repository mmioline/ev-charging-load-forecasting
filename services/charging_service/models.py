from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class ChargingRecord(Base):
    __tablename__ = "charging_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
 
    user_id = Column(String(50), nullable=False) 
    station_id = Column(Integer, nullable=False)
    kwh_consumed = Column(Integer, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())