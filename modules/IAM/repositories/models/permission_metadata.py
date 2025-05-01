from sqlalchemy import Column, Integer
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import String
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base


class PermissionMetadata(Base):
    __tablename__ = 'iot-permission-metadata'
    id = Column(Integer, primary_key = True)
    resource = Column(String)
    action = Column(String)
    scope = Column(JSONB)
    action_type = Column(String)
    display_name = Column(String)
    module_id = Column(Integer)
 