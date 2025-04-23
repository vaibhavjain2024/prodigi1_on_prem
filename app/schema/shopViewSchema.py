from pydantic import BaseModel
from typing import Optional

class shopView(BaseModel):
    shop_id: int
    page_no: Optional[int] = None
    page_size: Optional[int] = None
    view: Optional[str] = None

class shopViewReport(BaseModel):
    shop_id: int
    view: Optional[str] = None
    machine_group: Optional[str] = None
    machine_name: Optional[str] = None

class shopViewGraph(BaseModel):
    shop_id: int
    view: Optional[str] = None
    machine_name: Optional[str] = None

class machineView(BaseModel):
    shop_id: int
    view: Optional[str] = None
    machine_group: Optional[str] = None
    machine_name: Optional[str] = None

class machineViewGraph(BaseModel):
    shop_id: int
    view: Optional[str] = None
    machine_name: Optional[str] = None

class uniquePartsCount(BaseModel):
    shop_id: int

class topBreakDown(BaseModel):
    shop_id: int
    machine_list: Optional[str] = None