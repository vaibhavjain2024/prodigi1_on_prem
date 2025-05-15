from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    Index,
    Float,
    ForeignKey
)
from ..db_setup import Base

class MSILDowntimeFilter(Base):
    __tablename__ = 'iot-psm-msil-get-downtime-filter'
    __table_args__ = {'extend_existing': True}
    material_code = Column(String, primary_key = True)
    part_name = Column(String)
    model_id = Column(Integer, ForeignKey("iot-psm-msil-model.id"), index=True)
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)
    reason_id = Column(Integer,  ForeignKey('iot-psm-msil-downtime-reasons'), index=True)
    remark_id = Column(Integer,  ForeignKey('iot-psm-msil-downtime-remarks'), index=True)
    comment = Column(String)
    shift = Column(String)
    shop_id = Column(Integer, default=3)
    updated_by = Column(String, default = None)