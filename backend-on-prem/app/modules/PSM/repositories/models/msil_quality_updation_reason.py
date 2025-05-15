from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    func,
    Index,
    Enum,
    Boolean
)
from sqlalchemy.dialects.postgresql import JSONB
import enum
from ..db_setup import Base


class ReworkEvaluationTypeEnum(enum.Enum):
    REJECT=0
    RECYLCE=1
    OK=2

class MSILQualityUpdationReasons(Base):
    __tablename__ = 'iot-psm-msil-quality-updation-reasons'
    __table_args__ =  {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    reason = Column(String)
    type = Column(Enum(ReworkEvaluationTypeEnum))
    shop_id = Column(Integer)
    is_deleted = Column(Boolean)