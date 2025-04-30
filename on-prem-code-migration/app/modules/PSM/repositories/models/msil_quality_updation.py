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

class MSILQualityUpdation(Base):

    __tablename__ = 'iot-psm-msil-quality-updation'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    quality_punching_id = Column(Integer, ForeignKey('iot-psm-msil-quality-punching.id'), index=True)
    rework_qty = Column(Integer)
    pending_rework_qty = Column(Integer)
    reject_qty = Column(Integer)
    recycle_qty = Column(Integer)
    ok_qty = Column(Integer)
    status = Column(String)
