from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class ChargingRecord(Base):
    __tablename__ = "charging_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
 
    user_id = Column(String(50), nullable=False) 
    station_id = Column(Integer, nullable=False)
    kwh_consumed = Column(Float, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String(20), nullable=False, default="空闲", server_default="空闲")
    last_updated_at = Column(DateTime, nullable=False, server_default=func.now())
