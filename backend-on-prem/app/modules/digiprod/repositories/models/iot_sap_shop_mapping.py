from ..db_setup import Base
from sqlalchemy import Column, Integer, String


class iotSAPplantShopMapping(Base):

    __tablename__ = "iot_sap_plant_shop_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iot_plant_id = Column(Integer, nullable=False)
    sap_plant_id = Column(Integer, nullable=False)
    iot_shop_id = Column(Integer, nullable=False)
    sap_shop_id = Column(String, nullable=False)
