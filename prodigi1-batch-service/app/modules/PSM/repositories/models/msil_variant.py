from sqlalchemy import (
    Integer,
    Column,
    String,
    Index,
)
from ..db_setup import Base

class MSILVariant(Base):
    __tablename__ = 'iot-psm-msil-variant'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    variant_name = Column(String)
    common_name = Column(String)