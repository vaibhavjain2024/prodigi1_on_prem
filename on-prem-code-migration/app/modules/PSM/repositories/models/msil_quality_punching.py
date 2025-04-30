from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base


class MSILQualityPunching(Base):
    __tablename__ = 'iot-psm-msil-quality-punching'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    material_code =  Column(String, index=True)
    batch_id = Column(Integer, ForeignKey('iot-psm-msil-batch.id'), index=True)
    hold_qty = Column(Integer)
    reject_qty = Column(Integer)
    rework_qty = Column(Integer)
    ok_qty = Column(Integer)
    status = Column(String)
    submitted_by = Column(String)
    submitted_at = Column(DateTime)
    shop_id = Column(Integer, default=3)
