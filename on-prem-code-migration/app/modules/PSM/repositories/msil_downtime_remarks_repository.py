from .models.msil_downtime_remark import MSILDowntimeRemarks
from .models.msil_downtime_reason import MSILDowntimeReasons
from datetime import timedelta
from .repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import Integer


class MSILDowntimeRemarkRepository(Repository):
    """MSILLineRepository to manage MSILLine data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILDowntimeRemarks

    # def get_remark_list(self,id):
    #     with self.session:
    #         try:
    #             query = (
    #                 self.session.query( MSILDowntimeReasons.reason,self.model_type.remark)
    #                 .join(MSILDowntimeReasons, self.model_type.reason_id.cast(Integer) == MSILDowntimeReasons.id)
    #                 .filter(MSILDowntimeReasons.id == id)
    #                 .all()
    #             )
    #             remark_list = [row[1] for row in query]
    #             return remark_list
    #         except:
    #             return Exception

    

    def get_remark_list(self, shop_id):
        try:
            
            query = (
                self.session.query(MSILDowntimeReasons.id, MSILDowntimeReasons.reason, MSILDowntimeRemarks.remark)
                .join(MSILDowntimeReasons, self.model_type.reason_id.cast(Integer) == MSILDowntimeReasons.id)
                .filter(MSILDowntimeReasons.shop_id == shop_id)
                .all()
            )
            
            remarks_by_reason = {}
            
            for item in query:
                reason_id, reason, remark = item
                if reason_id not in remarks_by_reason:
                    remarks_by_reason.setdefault(reason, []).append(remark)
            
            return remarks_by_reason
        
        except Exception as e:
           
            raise e
    
    def check_and_add_remark(self,reason,remark):
        with self.session:
            remark_format = str(remark).strip().capitalize()
            result = self.session.query(self.model_type).filter(self.model_type.reason_id==str(reason),
                                                                self.model_type.remark==remark_format).first()
            if not result:
                new_remark = MSILDowntimeRemarks()
                new_remark.reason_id = str(reason)
                new_remark.remark = remark_format
                self.add(new_remark)
            