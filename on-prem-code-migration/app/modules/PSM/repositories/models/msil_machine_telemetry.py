from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    ForeignKey
)
from ..db_setup import Base

class MSILMachineTelemetry(Base):
    __tablename__ = 'iot-psm-msil-machine-telemetry'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True )
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    # material_code =  Column(String,  ForeignKey('iot-psm-msil-part.material_code'), index=True)
    material_code =  Column(String, index=True)
    timestamp = Column(DateTime)
    quantity = Column(Integer)
    station_counter_type = Column(Integer)