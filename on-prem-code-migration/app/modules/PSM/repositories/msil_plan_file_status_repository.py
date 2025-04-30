from .repository import Repository
from .models.msil_plan_file_status import MSILPlanFileStatus
from sqlalchemy.orm import Session
from sqlalchemy import desc

class MSILPlanFileStatusRepository(Repository):
    """MSILPlanFileStatusRepository to manage MSILLine data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILPlanFileStatus
    
    def new_status(self, date, status, error, shop):
        with self.session:
            result = self.session.query(self.model_type).filter(self.model_type.plan_for_date == date).filter(self.model_type.shop_id == shop).first()
            if result:
                result.errors = error
                result.status = status
                self.commit()
            else:
                new = MSILPlanFileStatus()
                new.plan_for_date = date
                new.shop_id = shop
                new.status = status
                new.errors = error
                self.add(new)
            return True
    
    # def filter_by(self, **filters):
    #     with self.session:
    #         return self.session.query(self.model_type).filter_by(**filters).order_by(desc(self.model_type.plan_for_date)).first()