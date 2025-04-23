from pydantic import BaseModel
from typing import Optional

class getQuality(BaseModel):
    shop_id: int
    page_no: int
    page_size: int
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    batch: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    shift: Optional[str] = None
    status: Optional[str] = None

class updateRecord(BaseModel):
    punching_id: int
    updation_list: list

class addRecord(BaseModel):
    punching_id: int

class getRecord(BaseModel):
    punching_id: int

class reworkTotal(BaseModel):
    shop_id: int
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    batch: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    shift: Optional[str] = None
    status: Optional[str] = None

class getReport(BaseModel):
    shop_id: int
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    batch: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    shift: Optional[str] = None
    status: Optional[str] = None