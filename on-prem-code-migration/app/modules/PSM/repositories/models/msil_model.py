from sqlalchemy import (
    Integer,
    Float,
    Column,
    Index,
    String)
from ..db_setup import Base

class MSILModel(Base):
    __tablename__ = 'iot-psm-msil-model'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    model_name = Column(String)
    model_description = Column(String)
    shop_id = Column(Integer, index=True)