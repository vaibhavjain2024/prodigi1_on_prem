import enum
from ..db_setup import Base
from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    Enum
)


class SAPPlanLogStatusEnum(enum.Enum):
    ORDER_SAVED = "ORDER_SAVED"
    ORDER_ACCEPTED = "ORDER_ACCEPTED"
    ORDER_REJECTED = "ORDER_REJECTED"


class PlanSAPLogs(Base):

    __tablename__ = "iot_sap_logs_plan"

    id = Column(Integer, primary_key=True, nullable=False)
    data_received_time = Column(DateTime)
    filename = Column(String, nullable=False)
    order_number = Column(String, nullable=False)
    order_status = Column(String, nullable=False)
    order_type = Column(String)
    mrp_controller = Column(String, nullable=False)
    plant = Column(String, nullable=False)
    work_center = Column(String, nullable=False)
    scheduled_finish = Column(DateTime, nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    production_version = Column(String)
    header_material = Column(String, nullable=False)
    group = Column(String)
    total_order_quantity = Column(String, nullable=False)
    header_stock = Column(String)
    order_UoM = Column(String)
    header_Sloc = Column(String)
    item_number = Column(String, nullable=False)
    components = Column(String, nullable=False)
    issue_quantity = Column(String, nullable=False)
    comp_stock = Column(String)
    comp_Uom = Column(String)
    comp_Sloc = Column(String)
    co_product = Column(String)
    iot_order_processing_status = Column(Enum(SAPPlanLogStatusEnum))
    iot_shop_id = Column(Integer)
