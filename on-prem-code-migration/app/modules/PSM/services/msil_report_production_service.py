from ..repositories.msil_report_production_repository import MSILReportProductionRepository
from ..repositories.msil_production_repository import MSILProductionRepository
from ..repositories.models.msil_production import MSILProduction
from ..repositories.models.msil_part import MSILPart
from .service import Service
import datetime
from .shift_util import get_shift, get_production_date
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')
class MSILReportProductionService(Service):
    def __init__(self, repository : MSILProductionRepository):
        super().__init__(repository, self.transform_model_to_dict, 
                         self.transform_dict_to_model)
        self.repository = repository