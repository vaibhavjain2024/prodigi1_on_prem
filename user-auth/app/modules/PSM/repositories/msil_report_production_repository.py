from app.modules.PSM.repositories.models.msil_alert_notification import AlertNotification
from app.modules.PSM.repositories.models.msil_part import MSILPart
from app.modules.PSM.repositories.models.msil_production import MSILProduction, ProductionStatusEnum
from app.modules.PSM.repositories.models.msil_batch import MSILBatch
from app.modules.PSM.repositories.models.msil_shift import MSILShift
from app.modules.PSM.repositories.models.msil_shop_breaks import MSILShopBreaks
from app.modules.PSM.repositories.models.msil_input_material import MSILInputMaterial
from app.modules.PSM.repositories.models.msil_equipment import MSILEquipment
from app.modules.PSM.repositories.models.msil_downtime import MSILDowntime
from app.modules.PSM.repositories.models.msil_downtime_reason import MSILDowntimeReasons
from app.modules.PSM.repositories.models.msil_model import MSILModel
from app.modules.PSM.repositories.models.msil_part import MSILPart
from app.modules.PSM.repositories.models.msil_variant import MSILVariant
from app.modules.PSM.repositories.models.msil_plan import MSILPlan, PlanStatusEnum
from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from .repository import Repository
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case,
    or_,
    String
)
from sqlalchemy.orm import aliased
import datetime
import pytz
ist_tz = pytz.timezone('Asia/Kolkata')

class MSILReportProductionRepository(Repository):
    """
    MSILProductionRepository to manage MSILMachine data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILProduction
