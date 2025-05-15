from sqlalchemy import (
     Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base


class MSILBatch(Base):
    __tablename__ = 'iot-psm-msil-batch'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    name = Column(String)
    shift = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    prod_qty = Column(Integer)
    input_id = Column(String)
    output_id = Column(String)
    production_id = Column(Integer, ForeignKey('iot-psm-msil-production.id'), index=True)
    material_code =  Column(String, index=True)
    SPM = Column(Integer)
