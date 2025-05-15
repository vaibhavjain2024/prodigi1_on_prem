from sqlalchemy import Column, Integer, String, DateTime, func, Enum, JSON
from IAM.repositories.db_setup import Base
from IAM import constants

class UserUploadLog(Base):
    __tablename__ = 'iot-user-upload-tracker'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    status = Column(Enum(constants.UserUploadFileStatusEnum))
    upload_report = Column(JSON)
    created_at = Column(DateTime, default=func.now(),)
    created_by = Column(String)
