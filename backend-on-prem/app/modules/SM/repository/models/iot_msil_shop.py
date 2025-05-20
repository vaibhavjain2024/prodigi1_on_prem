from sqlalchemy import Column, ForeignKey, Integer ,Table
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .iot_module_shop_association_table import IOTModuleShopAssociation


class MSILShop(Base):
    __tablename__ = 'iot-msil-shop'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    shop_name = Column(String)
    shop_type = Column(String)
    plant_id = Column(Integer, ForeignKey('iot-msil-plant.id'), index=True)
    modules = relationship("IOTModuleShopAssociation")
