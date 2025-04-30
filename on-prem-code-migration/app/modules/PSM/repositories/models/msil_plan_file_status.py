from sqlalchemy import (
    Integer,
    Column,
    String,
    Date,
    Index,
    ForeignKey,
    Enum,
    Boolean
)
import enum 
import datetime
from ..db_setup import Base

class PlanFileStatusEnum(enum.Enum):
    SUCCESS = 0
    FAILED = 1
    INPROGRESS = 2


class MSILPlanFileStatus(Base):
    __tablename__ = 'iot-psm-msil-plan-file-status'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    status = Column(Enum(PlanFileStatusEnum))
    errors = Column(String)
    plan_for_date = Column(Date)
    shop_id = Column(Integer)