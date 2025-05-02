from modules.PSM.repositories.models.msil_quality_updation_reason import MSILQualityUpdationReasons, ReworkEvaluationTypeEnum
from .repository import Repository
from sqlalchemy.orm import Session
from collections import defaultdict
from sqlalchemy import (
    and_,
    desc,
    func,
    case
)
from sqlalchemy.sql.expression import true

class MSILQualityUpdationReasonRepository(Repository):
    """
    MSILQualityUpdationReasonRepository to manage MSILQualityUpdationReason data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILQualityUpdationReasons
        self.dict ={
            "OK":ReworkEvaluationTypeEnum.OK,
            "RECYCLE":ReworkEvaluationTypeEnum.RECYLCE,
            "REJECT":ReworkEvaluationTypeEnum.REJECT
        }
    
    def check_and_add_reason(self,reason,type,shop_id):
        with self.session:
            result = self.session.query(self.model_type).filter(
            self.model_type.shop_id==shop_id,
            self.model_type.reason == reason,
            self.model_type.type == self.dict[str(type).strip().upper()]
            ).first()
            if not result:
                new_reason = MSILQualityUpdationReasons()
                new_reason.shop_id = shop_id
                new_reason.reason = reason
                new_reason.type = self.dict[str(type).strip().upper()]
                new_reason.is_deleted = False
                self.add(new_reason)
            else:
                result.is_deleted=False
            self.session.commit()

    def delete_reasons(self,shop_id):
        with self.session:
            self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).update({self.model_type.is_deleted:True})
            self.session.commit()

        


   