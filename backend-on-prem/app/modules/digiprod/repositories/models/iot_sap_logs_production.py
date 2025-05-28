import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from ..db_setup import Base


class SAPLogProductionStatusEnum(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class ProductionSAPLogs(Base):

    __tablename__ = "iot_sap_logs_production"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine = Column(String)  # SAP Equipment ID
    program_no = Column(String)
    program_name = Column(String)
    model = Column(String)
    shift = Column(String)  # A/B/C
    data_capture_time = Column(DateTime)  # First push attempt time
    data_update_time = Column(DateTime)  # Latest push/repush attempt
    status = Column(Enum(SAPLogProductionStatusEnum))
    error_remarks = Column(Text)


class Config:
    orm_mode = True
