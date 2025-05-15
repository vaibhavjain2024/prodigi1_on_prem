from sqlalchemy import (
    Integer,
    Column,
    String,
    Boolean,
    ForeignKey)
from ..db_setup import Base

class MSILEquipment(Base):
    __tablename__ = 'iot-psm-msil-equipment'
    __table_args__ = {'extend_existing': True}
    id = Column(String, primary_key = True)
    name = Column(String)
    status = Column(String)
    SPM = Column(Integer)
    efficiency = Column(Integer)
    equipment_group = Column(String)
    description = Column(String)
    make = Column(String)
    capacity = Column(Integer)
    capacity_uom = Column(String)
    purchase_year = Column(Integer)
    # line_id = Column(Integer, ForeignKey("iot-psm-msil-line.id"), index = True)
    line_id = Column(Integer)
    # strokes = Column(Integer)
    # SPH = Column(Integer)
    is_deleted = Column(Boolean)
    shop_id = Column(Integer, index=True)