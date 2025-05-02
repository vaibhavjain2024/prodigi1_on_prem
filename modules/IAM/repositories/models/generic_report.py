from sqlalchemy import Column, Integer, JSON, DateTime, func, Enum
from sqlalchemy.types import String
from ..db_setup import Base
import enum

class ReportStatus(enum.Enum):
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"
    IN_PROGRESS = "IN_PROGRESS"
    INITIATED = "INITIATED"

class GenericReport(Base):
    __tablename__ = 'iot-generic-reports'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    report_type = Column(String)
    description = Column(String)
    download_url = Column(String)
    status = Column(Enum(ReportStatus))
    created_at = Column(DateTime, default=func.now(),)

    def __repr__(self):
        return f'ID_{self.id}-ReportType_{self.report_type}-DESCRIPTION_{self.description}-STATUS_{self.status}-URL_{self.download_url}'