from sqlalchemy import (
    Integer,
    Column,
    String,
    JSON,
    ForeignKey,
    Index,
    Boolean
)
from ..db_setup import Base

class MSILRecipe(Base):
    __tablename__ = 'iot-psm-msil-recipe'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    equipment_id = Column(String,  ForeignKey('iot-psm-msil-equipment.id'), index=True)
    data_number = Column(String)
    data_number_description = Column(String)
    input_1 = Column(String,  index=True)
    input_1_qty = Column(Integer)
    input_2 = Column(String, index=True)
    input_2_qty = Column(Integer)
    output_1 = Column(String, index=True)
    output_1_qty = Column(Integer)
    output_2 = Column(String, index=True)
    output_2_qty = Column(Integer)
    die_obj = Column(JSON)
    # variant = Column(Boolean)
    input_storage_unit_group = Column(String)
    output_storage_unit_group = Column(String)
    shop_id = Column(Integer, index=True)

