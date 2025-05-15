from pydantic import BaseModel
from typing import Optional

class getQuality(BaseModel):
    shop_id: str
    page_no: int
    page_size: int
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    batch: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    hold_qty: Optional[int] = None
    shift: Optional[str] = None
    status: Optional[str] = None

class getQualityReport(BaseModel):
    shop_id: str
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    batch: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    hold_qty: Optional[int] = None
    shift: Optional[str] = None
    status: Optional[str] = None

class getQualityFilter(BaseModel):
    shop_id: str

class qualityPunching(BaseModel):
    punching_id: int

class updateQualityPunching(BaseModel):
    punching_id: int
    punching_list: list