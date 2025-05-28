from sqlalchemy import Column, ForeignKey, Integer ,Table
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .iot_module import IoTModule


class IOTModuleShopAssociation(Base):
    __tablename__ = 'iot-module-shop-association'
    __table_args__ = {'extend_existing': True}
    iot_module_id = Column(Integer, ForeignKey('iot-module.id') , primary_key = True)
    iot_msil_shop_id = Column(Integer, ForeignKey('iot-msil-shop.id') , primary_key = True)
    modules = relationship("IoTModule")