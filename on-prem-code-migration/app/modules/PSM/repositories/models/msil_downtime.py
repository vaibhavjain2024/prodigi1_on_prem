from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    func,
    Index,
    Numeric
)
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base


class MSILDowntime(Base):
    __tablename__ = 'iot-psm-msil-downtime'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    model_id = Column(Integer, ForeignKey('iot-psm-msil-model.id'), index=True)
    material_code =  Column(String, index=True)
    part_2_material_code = Column(String, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Numeric(precision=10, scale=2))
    reason_id = Column(Integer,  ForeignKey('iot-psm-msil-downtime-reasons.id'), index=True)
    remark_id = Column(Integer,  ForeignKey('iot-psm-msil-downtime-remarks.id'), index=True)
    comment = Column(String)
    shift = Column(String)
    shop_id = Column(Integer, default=3)
    updated_by = Column(String, default = None)