from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    Time,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base

class MSILShift(Base):

    __tablename__ = 'iot-psm-msil-shift'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    shop_id = Column(Integer)
    shift_name = Column(String)
    shift_start_timing = Column(Time)
    shift_end_timing = Column(Time)