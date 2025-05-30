from pydantic import BaseModel, Field
from typing import Optional

class getProductionQuality(BaseModel):
    shop_id: str
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


class UpdateVariantRequest(BaseModel):
    shop_id: str
    production_id: int
    prev_material_code: str
    material_code: str
    part: str


class getProductionFilter(BaseModel):
    shop_id: str
    production_id: int


class getProduction(BaseModel):
    shop_id: str
    equipment_id: str


class ShopIdSchema(BaseModel):
    shop_id: str = Field(..., description="The ID of the shop")