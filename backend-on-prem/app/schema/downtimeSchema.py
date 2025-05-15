from pydantic import BaseModel
from typing import Optional

class getDowntime(BaseModel):
    shop_id: str
    page_no: int = 1
    page_size: int = 10
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[str] = None
    shift: Optional[str] = None
    reason: Optional[str] = None
    remarks: Optional[str] = None
    

class getDowntimeReport(BaseModel):
    shop_id: str
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[str] = None
    shift: Optional[str] = None
    reason: Optional[str] = None
    remarks: Optional[str] = None


class getDowntimeFilter(BaseModel):
    shop_id: str


class updateDowntimeRemark(BaseModel):
    shop_id: str
    id: int
    remarks: str
    comment: str