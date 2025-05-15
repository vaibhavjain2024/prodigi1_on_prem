from sqlalchemy import (
    DateTime,
    Integer,
    Column,
    String
)
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base


class AlertNotification(Base):
    __tablename__ = 'iot-psm-msil-alert-notification'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    notification = Column(String) 
    created_at = Column(DateTime)
    alert_type = Column(String)
    notification_metadata = Column(JSONB)
    shop_id = Column(Integer, default=3)
    