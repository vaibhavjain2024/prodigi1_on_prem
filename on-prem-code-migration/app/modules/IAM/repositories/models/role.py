from sqlalchemy import Column, Integer
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint, Table
from sqlalchemy.types import String, Boolean
from ..db_setup import Base
from sqlalchemy.dialects.postgresql import JSONB



class Role(Base):
    __tablename__ = 'iot-role'
    
    id = Column(Integer, primary_key = True)
    name = Column(String)
    tenant = Column(String)
    parent_role_id = Column(Integer,ForeignKey('iot-role.id'), index=True)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)

