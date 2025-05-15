from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    func,
    Index,
    Boolean,
    Enum
)
from sqlalchemy.dialects.postgresql import JSONB
import enum
from ..db_setup import Base


class QualityEvaluationTypeEnum(enum.Enum):
    REJECT=0
    REWORK=1

class MSILQualityReasons(Base):
    __tablename__ = 'iot-psm-msil-quality-reasons'
    __table_args__ =  {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    reason = Column(String)
    type = Column(Enum(QualityEvaluationTypeEnum))
    shop_id = Column(Integer)
    is_deleted = Column(Boolean)