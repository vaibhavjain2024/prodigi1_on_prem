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
    data_sent_time: Optional[datetime] = Field(
        default=None, description="Timestamp when data was sent to SAP"
    )
    data_sent_flag: Optional[SAPLogStatusEnum] = Field(
        default=None, description="Status of data sent to SAP (PENDING, SUCCESS, FAILED)"
    )
    sap_plant_id: Optional[int] = Field(
        default=None, description="SAP plant identifier"
    )
    sap_shop_id: Optional[str] = Field(
        default=None, description="SAP shop identifier"
    )
    header_material: Optional[str] = Field(
        default=None, description="Header material code from SAP"
    )
    program_no: Optional[str] = Field(
        default=None, description="Program number running during the downtime"
    )
    work_center: Optional[str] = Field(
        default=None, description="SAP work center where downtime occurred"
    )
    start_time: Optional[datetime] = Field(
        default=None, description="Downtime start timestamp"
    )
    end_time: Optional[datetime] = Field(
        default=None, description="Downtime end timestamp"
    )
    duration: Optional[Decimal] = Field(
        default=None, description="Duration of downtime in hours (precision up to 2 decimal places)"
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for the downtime"
    )
    remarks: Optional[str] = Field(
        default=None, description="Additional remarks or notes"
    )
    shift: Optional[str] = Field(
        default=None, description="Shift during which the downtime occurred"
    )
    inserted_at: Optional[datetime] = Field(
        default=None, description="Timestamp when this log was inserted"
    )


# class getSapDowntimeReport(BaseModel):
#     shop_id: str
#     model_list: Optional[str] = None
#     machine_list: Optional[str] = None
#     part_name_list: Optional[str] = None
#     start_time: Optional[str] = None
#     end_time: Optional[str] = None
#     duration: Optional[str] = None
#     shift: Optional[str] = None
#     reason: Optional[str] = None
#     remarks: Optional[str] = None
