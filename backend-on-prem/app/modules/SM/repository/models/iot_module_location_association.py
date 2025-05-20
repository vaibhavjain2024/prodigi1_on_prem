from sqlalchemy import Column, ForeignKey, Integer ,Table
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .iot_module import IoTModule



class IOTModuleLocationAssociation(Base):
    __tablename__ = 'iot-module-location-association'
    __table_args__ = {'extend_existing': True}
    iot_module_id = Column(Integer, ForeignKey('iot-module.id') , primary_key = True)
    iot_msil_location_id = Column(Integer, ForeignKey('iot-msil-location.id') , primary_key = True)
    modules = relationship("IoTModule")