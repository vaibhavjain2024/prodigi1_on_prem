from sqlalchemy import Column, ForeignKey, Integer 
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .iot_msil_plant import MSILPlant


class MSILLocation(Base):
    __tablename__ = 'iot-msil-location'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    location_name = Column(String)
    plants = relationship("MSILPlant", lazy='joined')
    site_id = Column(Integer, ForeignKey('iot-msil-site.id'), index=True)