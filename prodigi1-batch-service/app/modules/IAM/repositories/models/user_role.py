from sqlalchemy import Column, Integer
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint, Table
from ..db_setup import Base
from sqlalchemy.orm import relationship


class UserRole(Base):
    __tablename__ = 'iot-user-role'

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id'],
            ['iot-user.id']
        ),
        ForeignKeyConstraint(
            ['role_id'],
            ['iot-role.id']
        ),
)

    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)
    role = relationship('Role')