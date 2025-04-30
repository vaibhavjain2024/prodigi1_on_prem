from sqlalchemy import (
    Integer,
    Column,
    String,
    Date,
    Index,
    Float,
    ForeignKey,
    Enum
)

from ..db_setup import Base
import enum

class MSILInputMaterial(Base):
    __tablename__ = 'iot-psm-msil-input_material'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    part_name = Column(String, index=True)
    production_id = Column(Integer, ForeignKey('iot-psm-msil-production.id'), index=True)
    batch_id = Column(Integer, ForeignKey("iot-psm-msil-batch.id"), index=True)
    details = Column(String)
    thickness = Column(Float)
    width = Column(Float)
    material_qty = Column(Integer)