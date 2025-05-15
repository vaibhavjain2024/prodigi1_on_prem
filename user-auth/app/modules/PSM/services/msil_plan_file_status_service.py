import datetime
from ..repositories.msil_plan_file_status_repository import MSILPlanFileStatusRepository
from ..repositories.models.msil_plan_file_status import MSILPlanFileStatus, PlanFileStatusEnum
import pytz

class MSILPlanFileStatusService:
    def __init__(self, repository: MSILPlanFileStatusRepository):
        self.repository = repository

    def get_file_status(self, shop_id, date):
        filters = {'shop_id':shop_id, 'plan_for_date':date}
        status = self.repository.filter_by(**filters)

        if status is not None:
            status_obj = {
                'shop_id': status.shop_id,
                'plan_for_date': status.plan_for_date,
                'status': str(status.status).replace("PlanFileStatusEnum.",""),
                'errors': status.errors
            }
            if status.status == PlanFileStatusEnum.FAILED:
                self.repository.remove(status.id)
        else:
            status_obj = None
        return status_obj
