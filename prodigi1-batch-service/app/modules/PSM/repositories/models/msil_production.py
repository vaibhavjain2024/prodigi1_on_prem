from sqlalchemy import (
    Integer,
    Column,
    String,
    Date,
    Index,
    Float,
    ForeignKey,
    Enum,
    Boolean
)

from ..db_setup import Base
import enum

class ProductionStatusEnum(enum.Enum):
    RUNNING=0
    PAUSED=1
    FINISHED=2

class MSILProduction(Base):
    __tablename__ = 'iot-psm-msil-production'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    is_down = Column(Boolean)
    date = Column(Date)
    shift = Column(String)
    status = Column(Enum(ProductionStatusEnum))
    part_1 = Column(String, index=True)
    part_2 = Column(String, index=True)