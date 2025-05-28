from sqlalchemy import Column, ForeignKey, Integer 
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .iot_msil_shop import MSILShop


class MSILPlant(Base):
    __tablename__ = 'iot-msil-plant'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    plant_name = Column(String)
    shops = relationship("MSILShop", lazy='joined')
    location_id = Column(Integer, ForeignKey('iot-msil-location.id'), index=True)