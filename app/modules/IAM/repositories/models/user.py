from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.types import String
from .user_role import UserRole
from sqlalchemy.orm import relationship
from ..db_setup import Base
from sqlalchemy.sql.schema import ForeignKey, Table

class User(Base):
    __tablename__ = 'iot-user'
    id = Column(Integer, primary_key = True)
    federation_identifier = Column(String)
    tenant = Column(String)
    last_loggedin = Column(BigInteger)
    roles = relationship("UserRole")