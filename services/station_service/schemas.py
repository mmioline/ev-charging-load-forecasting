from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional

class StationStatus(str, Enum):
    available = "空闲"
    charging = "充电中"
    abnormal = "异常"
    fault = "故障"

class StationBase(BaseModel):
    name: str
    location: Optional[str] = None
    capacity: float  # 总功率
    slots: int      # 桩位数量

class StationCreate(StationBase):
    pass

class StationOut(StationBase):
    id: int
    status: StationStatus
    last_updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StationStatusUpdate(BaseModel):
    status: StationStatus

class StationStatusOut(BaseModel):
    station_id: int
    status: StationStatus
    last_updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
