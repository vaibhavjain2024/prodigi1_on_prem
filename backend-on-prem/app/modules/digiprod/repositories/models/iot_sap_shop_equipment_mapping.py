from ..db_setup import Base
from sqlalchemy import Column, Integer, String


class iotSAPshopEquipmentMapping(Base):

    __tablename__ = "iot_sap_shop_equipment_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    iot_shop_id = Column(Integer, nullable=False)
    iot_equipment_id = Column(String, nullable=False)
    sap_work_center = Column(String, nullable=False)
