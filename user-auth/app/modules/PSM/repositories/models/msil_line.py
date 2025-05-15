from sqlalchemy import (
    Integer,
    Column,
    String,
    Index
)
from ..db_setup import Base

class MSILLine(Base):
    __tablename__ = 'iot-psm-msil-line'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    name = Column(String)
    shop_id = Column(Integer, index=True)
    idx_line_name = Index('idx_line_name_psm', name)
    