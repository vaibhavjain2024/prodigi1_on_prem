from ntpath import join
from sqlalchemy import Column, Integer ,Table, ForeignKey
from sqlalchemy.types import String
from ..db_setup import Base


class IoTModule(Base):
    __tablename__ = 'iot-module'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    module_name = Column(String)
    display_name = Column(String)

    def __unicode__(self):
        return "Id: " + self.id + " Module name: " + self.module_name
