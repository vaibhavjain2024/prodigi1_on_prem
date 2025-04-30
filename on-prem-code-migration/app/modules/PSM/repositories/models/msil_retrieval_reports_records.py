import enum
from sqlalchemy import (
    Integer,
    Column,
    String,
    Enum,
    DateTime
)

from ..db_setup import Base

class ReportStatus(enum.Enum):
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"
    IN_PROGRESS = "IN PROGRESS"
    INITIATED = "INITIATED"


class MSILRetrievalReportsRecords(Base):
    __tablename__ = 'iot-psm-msil-retrieval-reports-records'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    module = Column(String)
    table = Column(String)
    description = Column(String)
    download_url = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(ReportStatus))

    def __repr__(self):
        return f'ID_{self.id}-ModuleName_{self.module}-TableName_{self.table}-DESCRIPTION_{self.description}-STATUS_{self.status}-URL_{self.download_url}-StartDate_{self.start_date}-EndDate_{self.end_date}'
