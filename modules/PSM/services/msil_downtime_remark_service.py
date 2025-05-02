from ..repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from ..repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from ..repositories.models.msil_downtime import MSILDowntime
from ..repositories.models.msil_downtime import MSILDowntime

class MSILDowntimeRemarkService:
    def __init__(self, repository: MSILDowntimeRemarkRepository, reason_repo: MSILDowntimeReasonRepository):
        self.repository = repository
        self.reason_repository = reason_repo

    
    def get_remarks_with_reasons_id(self, shop_id):

        remarks_list = self.repository.get_remark_list(shop_id = shop_id)

        return remarks_list

