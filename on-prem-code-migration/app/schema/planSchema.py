from pydantic import BaseModel, Field
from typing import Optional

class getPlan(BaseModel):
    shop_id: int
    page_no: int = 1
    page_size: int = 10
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    pe_code_list: Optional[str] = None
    production_date_list: Optional[str] = None
    shift: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    sort_priority: Optional[str] = None
    

class getPlanReport(BaseModel):
    shop_id: int
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    pe_code_list: Optional[str] = None
    production_date_list: Optional[str] = None
    shift: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    sort_priority: Optional[str] = None


class getPlanFilter(BaseModel):
    shop_id: int


class planDownload(BaseModel):
    shop_id: int = Field(..., description="The ID of the shop")
    shop_name: Optional[str] = Field(None, description="The name of the shop")
    date: Optional[str] = None


class planUpload(BaseModel):
    shop_id: int = Field(..., description="The ID of the shop")
    shop_name: Optional[str] = None