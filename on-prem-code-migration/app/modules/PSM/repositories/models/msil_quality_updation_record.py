from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    Boolean,
    Enum,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB
import enum
from ..db_setup import Base

class ReworkEvaluationEnum(enum.Enum):
    REJECT=0
    RECYCLE=1
    OK=2

class MSILQualityUpdationRecord(Base):
    __tablename__ = 'iot-psm-msil-quality-updation-record'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    quality_updation_id = Column(Integer, ForeignKey('iot-psm-msil-quality-updation.id'), index=True)
    quantity = Column(Integer)
    evaluation = Column(Enum(ReworkEvaluationEnum))
    remark_id = Column(Integer, ForeignKey('iot-psm-msil-quality-updation-remarks.id'), index=True)
    created_at = Column(DateTime)
    created_by = Column(String)
    updated_at = Column(DateTime)
    updated_by = Column(String)
    is_deleted = Column(Boolean)