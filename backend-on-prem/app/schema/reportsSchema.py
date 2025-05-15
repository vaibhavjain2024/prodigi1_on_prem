from pydantic import BaseModel
from typing import Optional

class reportFilter(BaseModel):
    shop_id: int

class Reports(BaseModel):
    shop_id: int
    start_date: str
    end_date: str
    model_list: Optional[str] = None
    machine_list: Optional[str] = None
    part_name_list: Optional[str] = None
    shift: Optional[str] = None
