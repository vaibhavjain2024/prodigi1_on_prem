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

class MSILQualityRemarks(Base):
    __tablename__ = 'iot-psm-msil-quality-remarks'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    reason_id = Column(Integer,  ForeignKey('iot-psm-msil-quality-reasons.id'), index=True)
    remark = Column(String)