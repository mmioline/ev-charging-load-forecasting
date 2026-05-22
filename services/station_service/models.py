from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func
from .database import Base

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False)
    location = Column(String(255))
    capacity = Column(Float, nullable=False)
    slots = Column(Integer, default=0)
    status = Column(String(20), nullable=False, default="空闲", server_default="空闲")
    last_updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
