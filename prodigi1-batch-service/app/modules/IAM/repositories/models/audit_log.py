from sqlalchemy import Column, Integer, JSON, DateTime, func
from sqlalchemy.types import String
from ..db_setup import Base


class AuditLog(Base):
    __tablename__ = 'iot-audit-log'
    id = Column(Integer, primary_key = True)

    http_method = Column(String)
    request_path = Column(String)
    module_name = Column(String)
    feature = Column(String)
    shop_id = Column(Integer)
    location_id = Column(Integer)
    username = Column(String)
    event_details = Column(JSON)
    event_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now(),)
    