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

class MSILShopBreaks(Base):

    __tablename__ = 'iot-psm-msil-shop-breaks'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    shop_id = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)
    duration_minutes = Column(Integer)