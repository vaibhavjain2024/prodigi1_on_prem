from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

#create a new db session 
def get_session(session, engine):

    from .models.msil_line import MSILLine
    from .models.msil_equipment import MSILEquipment
    from .models.msil_model import MSILModel
    from .models.msil_part import MSILPart
    from .models.msil_recipe import MSILRecipe
    from .models.msil_plan import MSILPlan
    from .models.msil_variant import MSILVariant
    from .models.msil_plan_file_status import MSILPlanFileStatus
    from .models.msil_batch import MSILBatch
    from .models.msil_downtime import MSILDowntime
    from .models.msil_downtime_reason import MSILDowntimeReasons
    from .models.msil_downtime_remark import MSILDowntimeRemarks
    from .models.msil_quality_punching import MSILQualityPunching
    from .models.msil_quality_updation import MSILQualityUpdation
    from .models.msil_quality_reason import MSILQualityReasons
    from .models.msil_quality_remark import MSILQualityRemarks
    from .models.msil_quality_punch_record import MSILQualityPunchingRecord
    from .models.msil_quality_updation_record import MSILQualityUpdationRecord
    from .models.msil_quality_updation_reason import MSILQualityUpdationReasons
    from .models.msil_production import MSILProduction
    from .models.msil_input_material import MSILInputMaterial
    from .models.msil_shift import  MSILShift
    from .models.msil_shop_breaks import MSILShopBreaks
    from .models.msil_machine_telemetry import MSILMachineTelemetry
    from .models.msil_quality_updation_remarks import MSILQualityUpdationRemarks
    from .models.msil_alert_notification import AlertNotification
    from .models.msil_digiprod_master import MSILDigiprodMaster
    from .models.shop_configuration import ShopConfiguration
    from .models.msil_retrieval_reports_records import MSILRetrievalReportsRecords
    from .models.msil_iot_device_status import IOTDeviceStatus
    Base.metadata.create_all(engine)
    return session




