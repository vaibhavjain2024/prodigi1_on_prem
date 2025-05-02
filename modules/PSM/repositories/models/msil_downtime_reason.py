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

class MSILDowntimeReasons(Base):
    __tablename__ = 'iot-psm-msil-downtime-reasons'
    __table_args__ =  {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    reason = Column(String)
    reason_type = Column(String)
    tag = Column(String)
    shop_id = Column(Integer)