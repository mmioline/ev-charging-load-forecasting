from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ChargingRecordBase(BaseModel):
    station_id: int
    duration_minutes: int
    kwh_consumed: float

class ChargingRecordCreate(ChargingRecordBase):
    pass

class ChargingRecordOut(ChargingRecordBase):
    id: int
    user_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)