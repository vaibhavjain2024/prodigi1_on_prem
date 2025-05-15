from app.modules.PSM.repositories.models.msil_quality_reason import MSILQualityReasons, QualityEvaluationTypeEnum
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

class MSILQualityReasonRepository(Repository):
    """
    MSILQualityReasonRepository to manage MSILQualityReason data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILQualityReasons
        self.dict = {
            "REJECT":QualityEvaluationTypeEnum.REJECT,
            "REWORK":QualityEvaluationTypeEnum.REWORK
        }
    
    def check_and_add_reason(self,reason,type,shop_id):
        with self.session:
            result = self.session.query(self.model_type).filter(
            self.model_type.shop_id==shop_id,
            self.model_type.reason == reason,
            self.model_type.type == self.dict[str(type).strip().upper()]
            ).first()
            if not result:
                new_reason = MSILQualityReasons()
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



   