from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String
)
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from ..db_setup import Base

class IOTDeviceStatus(Base):
    __tablename__ = 'device_status'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(255), nullable=False, unique=True)
    event_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)