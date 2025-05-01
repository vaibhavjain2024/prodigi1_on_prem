from sqlalchemy import (
    Integer,
    Column,
    String,
    Date,
    Index,
    Float,
    ForeignKey
)
from ..db_setup import Base

class MSILPart(Base):
    __tablename__ = 'iot-psm-msil-part'
    __table_args__ = {'extend_existing': True}
    material_code = Column(String, primary_key = True)
    part_name = Column(String)
    #variant_id = Column(Integer, ForeignKey('iot-psm-msil-variant.id'), index=True)
    variant_id = Column(Integer)
    pe_code = Column(String)
    #model_id = Column(Integer, ForeignKey("iot-psm-msil-model.id"), index=True)
    model_id = Column(Integer)
    description = Column(String)
    material_type = Column(String)
    supplier = Column(String)
    storage_type = Column(String)
    unit = Column(String)
    thickness_nominal = Column(Float)
    thickness_upper = Column(Float)
    thickness_lower = Column(Float)
    thickness_tolerance_unit = Column(String)
    thickness_unit = Column(String)
    width_nominal = Column(Float)
    width_upper = Column(Float)
    width_lower = Column(Float)
    width_unit = Column(String)
    width_tolerance_unit = Column(String)
    weight = Column(Float)
    weight_unit = Column(String)    
    shop_id = Column(Integer)
    idx_part_name = Index('idx_part_name',part_name)