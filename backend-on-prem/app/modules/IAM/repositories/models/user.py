from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Boolean
from .user_session import IotUserSession

from ..db_setup import Base


class User(Base):
    __tablename__ = 'iot-user'

    id = Column(Integer, primary_key=True)
    federation_identifier = Column(String)

    tenant = Column(String)
    last_loggedin = Column(BigInteger)
    new_user = Column(Boolean, default=True)
    email_id = Column(String)
    mobile_number = Column(String, nullable=True)
    user_name = Column(String, nullable=True)

    roles = relationship("UserRole", lazy='joined')
    sessions = relationship("IotUserSession", back_populates="user", order_by="IotUserSession.login_time.desc()", lazy='dynamic')

    # # Newly added columns for tracking user login from platforms
    # token_timeout = Column(BigInteger, default=1800)
    # loggedin = Column(Boolean, default=False)
    #
    # platform = Column(String, default="WEB")
    # deviceId = Column(String, default=None)
