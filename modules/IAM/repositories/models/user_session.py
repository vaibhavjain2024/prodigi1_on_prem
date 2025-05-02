from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from ..db_setup import Base

class IotUserSession(Base):
    __tablename__ = 'iot-user-sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('iot-user.id'), nullable=False)
    login_time = Column(DateTime(timezone=True), nullable=False)
    logout_time = Column(DateTime(timezone=True), nullable=True)
    expected_expiry_time = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
