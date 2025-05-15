from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
    Index,
    Enum
)
import enum 
from ..db_setup import Base

class MasterFileStatusEnum(enum.Enum):
    # Master File Status:
    UPLOAD_IN_PROGRESS = "Upload In Progress"
    UPLOAD_FAILED = "Upload Failed"
    REVIEW_PENDING = "Review Pending"
    REJECTED = "Rejected"
    APPROVED = "Approved"

class MSILDigiprodMaster(Base):
    __tablename__ = 'iot-psm-msil-master'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    uploader_user_id = Column(String)
    uploader_user_name = Column(String)
    uploader_email = Column(String)
    upload_date_time = Column(DateTime)
    reviewer_id = Column(String)
    reviewer_name = Column(String)
    reviewer_email = Column(String)
    review_initiated_date = Column(DateTime)
    review_date = Column(DateTime)
    file_status = Column(Enum(MasterFileStatusEnum))
    master_file_path = Column(String)
    module_name = Column(String)
    shop_name = Column(String)
    plant_name = Column(String)
    site_location = Column(String)
    site_name = Column(String)
    version = Column(Integer)
    shop_id = Column(Integer)
    error_messages = Column(String)