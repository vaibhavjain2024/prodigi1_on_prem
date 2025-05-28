from sqlalchemy import Column, Integer 
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .iot_msil_location import MSILLocation


class MSILSite(Base):
    __tablename__ = 'iot-msil-site'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    site_name = Column(String)
    locations = relationship("MSILLocation")
