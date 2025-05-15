from sqlalchemy import (
    Integer,
    Column,
    String,
    Date,
    Index,
    ForeignKey,
    Enum,
    Boolean
)
import enum 
from ..db_setup import Base


class PlanStatusEnum(enum.Enum):
    PLANNED="PLANNED"
    RUNNING="RUNNING"
    PAUSED="PAUSED"
    SHORT_CLOSED="SHORT_CLOSED"
    COMPLETED="COMPLETED"
    UNPLANNED="UNPLANNED"


class MSILPlan(Base):
    __tablename__ = 'iot-psm-msil-plan'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True )
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    variant_id = Column(Integer, ForeignKey('iot-psm-msil-variant.id'), index=True)
    lot_size = Column(Integer)
    model_id =  Column(Integer, ForeignKey('iot-psm-msil-model.id'), index=True)
    material_code =  Column(String, index=True)
    work_order_number = Column(String)
    production_date = Column(Date)
    shift = Column(String)
    priority = Column(Integer)
    planned_quantity = Column(Integer)
    actual_quantity = Column (Integer)
    status = Column(Enum(PlanStatusEnum))
    shop_id = Column(Integer)
    # line_id = Column(Integer, ForeignKey('iot-psm-msil-line.id'), index=True)
    # part_id = Column(Integer, ForeignKey('iot-psm-msil-part.id'), index=True)
    idx_production_date = Index('idx_production_date', production_date)
    idx_priority = Index('idx_priority', priority)