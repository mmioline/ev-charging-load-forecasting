from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False)
    location = Column(String(255))
    capacity = Column(Float, nullable=False)
    slots = Column(Integer, default=0)