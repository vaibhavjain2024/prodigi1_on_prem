import enum
from ..db_setup import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Enum


class SAPLogStatusEnum(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class DowntimeSAPLogs(Base):

    __tablename__ = "iot_sap_downtime"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String)
    data_sent_time = Column(DateTime)
    data_sent_flag = Column(Enum(SAPLogStatusEnum))
    sap_plant_id = Column(Integer)
    sap_shop_id = Column(String)
    iot_shop_id = Column(String)
    header_material = Column(String)
    program_no = Column(String)
    work_center = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration = Column(Numeric(precision=10, scale=2), nullable=False)
    reason = Column(Text)
    remarks = Column(Text)
    shift = Column(String, nullable=False)
    inserted_at = Column(DateTime, nullable=False)


class Config:
    orm_mode = True
