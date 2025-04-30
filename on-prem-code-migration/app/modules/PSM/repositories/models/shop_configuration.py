from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    Time,
    func,
    Index,
    Boolean,
    JSON
)
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base

class ShopConfiguration(Base):

    __tablename__ = 'iot-psm-shop-configuration'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    shop_id = Column(Integer)
    is_shift = Column(Boolean)
    is_day = Column(Boolean)
    shop_timing = Column(JSON)
