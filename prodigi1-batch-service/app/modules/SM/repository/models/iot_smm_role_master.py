from sqlalchemy import Column, ForeignKey, Integer, Table, Boolean, Date
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base


class SMMRoleMaster(Base):
    __tablename__ = 'iot-smm-role-master'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey('iot-msil-shop.id'), index=True)
    shop_name = Column(String)
    plant_name = Column(String)
    plant_id = Column(Integer, ForeignKey('iot-msil-plant.id'), index=True)
    is_online = Column(Boolean, default=True)
    sub_category = Column(String)
    group_name = Column(String)
    line_name = Column(String)
    area_name = Column(String)
    area_supervisor_id = Column(String)
    line_incharge_id = Column(String)
    group_shift_incharge = Column(String)
    shop_safety_incharge = Column(String)
    shop_quality_incharge = Column(String)
    is_active = Column(Boolean, default=True)
    start_date = Column(Date)
    end_date = Column(Date)
    master_version = Column(Integer)
