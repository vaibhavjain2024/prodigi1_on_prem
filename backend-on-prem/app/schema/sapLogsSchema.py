from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SAPLogStatusEnum(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class DowntimeSAPLogs(BaseModel):
    filename: Optional[str] = Field(default=None)
    data_sent_time: Optional[datetime] = Field(default=None)
    data_sent_flag: Optional[SAPLogStatusEnum] = Field(default=None)
    sap_plant_id: Optional[int] = Field(default=None)
    sap_shop_id: Optional[str] = Field(default=None)
    iot_shop_id: Optional[str] = Field(default=None)
    header_material: Optional[str] = Field(default=None)
    program_no: Optional[str] = Field(default=None)
    work_center: Optional[str] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    duration: Optional[Decimal] = Field(default=None)
    reason: Optional[str] = Field(default=None)
    remarks: Optional[str] = Field(default=None)
    shift: Optional[str] = Field(default=None)
    inserted_at: Optional[datetime] = Field(default=None)


class PlanSAPLogs(BaseModel):
    id: Optional[int] = Field(default=None)
    data_received_time: Optional[datetime] = Field(default=None)
    filename: Optional[str] = Field(default=None)
    order_number: Optional[str] = Field(default=None)
    order_status: Optional[str] = Field(default=None)
    order_type: Optional[str] = Field(default=None)
    mrp_controller: Optional[str] = Field(default=None)
    plant: Optional[str] = Field(default=None)
    work_center: Optional[str] = Field(default=None)
    scheduled_finish: Optional[datetime] = Field(default=None)
    scheduled_start: Optional[datetime] = Field(default=None)
    production_version: Optional[str] = Field(default=None)
    header_material: Optional[str] = Field(default=None)
    group: Optional[str] = Field(default=None)
    total_order_quantity: Optional[str] = Field(default=None)
    header_stock: Optional[str] = Field(default=None)
    order_UoM: Optional[str] = Field(default=None)
    header_Sloc: Optional[str] = Field(default=None)
    item_number: Optional[str] = Field(default=None)
    components: Optional[str] = Field(default=None)
    issue_quantity: Optional[str] = Field(default=None)
    comp_stock: Optional[str] = Field(default=None)
    comp_Uom: Optional[str] = Field(default=None)
    comp_Sloc: Optional[str] = Field(default=None)
    co_product: Optional[str] = Field(default=None)
    iot_order_processing_status: Optional[SAPLogStatusEnum] = Field(
        default=None)
    iot_shop_id: Optional[str] = Field(default=None)
