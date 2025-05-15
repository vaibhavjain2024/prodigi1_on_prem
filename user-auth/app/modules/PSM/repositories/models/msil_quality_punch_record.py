from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    Boolean,
    func,
    Index,
    Enum
)
from sqlalchemy.dialects.postgresql import JSONB
import enum
from ..db_setup import Base

class QualityEvaluationEnum(enum.Enum):
    REJECT=0
    REWORK=1

class MSILQualityPunchingRecord(Base):
    __tablename__ = 'iot-psm-msil-quality-punching-record'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    quality_punching_id = Column(Integer, ForeignKey('iot-psm-msil-quality-punching.id'), index=True)
    quantity = Column(Integer)
    evaluation = Column(Enum(QualityEvaluationEnum))
    remark_id = Column(Integer, ForeignKey('iot-psm-msil-quality-remarks.id'), index=True)
    created_at = Column(DateTime)
    created_by = Column(String)
    updated_at = Column(DateTime)
    updated_by = Column(String)
    is_deleted = Column(Boolean)