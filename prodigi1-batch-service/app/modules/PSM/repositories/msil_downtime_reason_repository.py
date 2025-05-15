from .models.msil_downtime_reason import MSILDowntimeReasons
from datetime import timedelta
from .repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import and_

class MSILDowntimeReasonRepository(Repository):
    """MSILLineRepository to manage MSILLine data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILDowntimeReasons
    
    def reason_type_update(self,shop_id,combination_list):
        with self.session:
            for item in combination_list:
                result = self.session.query(self.model_type).filter(and_(self.model_type.shop_id==shop_id,
                                                                    self.model_type.tag==str(item[2]),
                                                                    self.model_type.reason_type == str(item[1]).strip().lower(),
                                                                    self.model_type.reason == str(item[0])
                                                                    )).first()
                if not result:
                    new_reason=MSILDowntimeReasons()
                    new_reason.shop_id=shop_id
                    new_reason.reason=str(item[0])
                    new_reason.reason_type=str(item[1]).strip().lower()
                    new_reason.tag=str(item[2])
                    self.add(new_reason)
                else:
                    result.reason = str(item[0])
                    result.reason_type = str(item[1]).strip().lower()
                    self.session.merge(result)
                    self.session.commit()
            return True
    
    def id_by_combination(self,shop_id):
        reason_dict = {}
        with self.session:
            result = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            for item in result:
                reason_dict[(item.reason,item.reason_type,item.tag)]=item.id
            return reason_dict
    
    def delete_reason_tags(self,shop_id, reason_ids):
        with self.session:
            self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id, self.model_type.id.in_(reason_ids)).update({self.model_type.tag:None})
            self.session.commit()
            return True
                


