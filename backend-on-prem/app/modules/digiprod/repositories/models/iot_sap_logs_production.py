from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from ..db_setup import Base
import enum


class SAPLogProductionStatusEnum(enum.Enum):
    IN_PROCESS = "IN_PROCESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class ProductionSAPLogAttempt(Base):
    __tablename__ = "iot_sap_logs_production_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(Integer, ForeignKey("iot_sap_logs_production.id"))
    attempt_number = Column(Integer, nullable=False)
    attempt_time = Column(DateTime, nullable=False)
    status = Column(Enum(SAPLogProductionStatusEnum))
    error_remarks = Column(Text)

    # Relationship to main production log
    log = relationship("ProductionSAPLogs", back_populates="attempts")


# Update existing ProductionSAPLogs to define the reverse relationship
class ProductionSAPLogs(Base):
    __tablename__ = "iot_sap_logs_production"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine = Column(String)
    sap_shop_id = Column(String)
    iot_shop_id = Column(String)
    program_no = Column(String)
    program_name = Column(String)
    model = Column(String)
    shift = Column(String)
    data_capture_time = Column(DateTime)
    data_update_time = Column(DateTime)
    status = Column(Enum(SAPLogProductionStatusEnum))
    error_remarks = Column(Text)
    batch_id = Column(String)

    # Relationship to attempts
    attempts = relationship("ProductionSAPLogAttempt", back_populates="log")
