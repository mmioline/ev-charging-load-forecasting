from pydantic import BaseModel, ConfigDict
from typing import Optional

class StationBase(BaseModel):
    name: str
    location: Optional[str] = None
    capacity: float  # 总功率
    slots: int      # 桩位数量

class StationCreate(StationBase):
    pass

class StationOut(StationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)