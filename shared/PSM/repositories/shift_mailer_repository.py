from datetime import timedelta
from modules.PSM.repositories.repository import Repository
from modules.PSM.repositories.models.msil_variant import MSILVariant
from sqlalchemy.orm import Session
from modules.PSM.repositories.models.msil_equipment import MSILEquipment
from modules.PSM.repositories.models.msil_alert_notification import AlertNotification
from modules.PSM.repositories.models.msil_batch import MSILBatch
from modules.PSM.repositories.models.msil_part import MSILPart
from modules.PSM.repositories.models.msil_model import MSILModel
from modules.PSM.repositories.models.msil_variant import MSILVariant
from modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from modules.PSM.repositories.models.msil_quality_punch_record import MSILQualityPunchingRecord
from modules.PSM.repositories.models.msil_quality_remark import MSILQualityRemarks
from modules.PSM.repositories.models.msil_input_material import MSILInputMaterial
from modules.PSM.repositories.models.msil_equipment import MSILEquipment
from modules.PSM.repositories.models.msil_downtime import MSILDowntime
from modules.PSM.repositories.models.msil_downtime_reason import MSILDowntimeReasons
from sqlalchemy import distinct
from sqlalchemy import Date, Interval, and_, case, cast, desc, distinct, func, Integer, literal, not_, or_, select, \
    tuple_, nullslast


class MSILShiftMailerRepository(Repository):
    """MSILLineRepository to manage MSILLine data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session

    def get_downtime_data_for_production_log_sheet(self,shop_id,shift_start_time,shift_end_time):
        with self.session:
            query = self.session.query(
                MSILDowntime.id,
                MSILPart.material_code.label('part_id'),
                MSILPart.part_name,
                MSILDowntime.equipment_id,
                MSILEquipment.name.label('equipment_name'),
                MSILDowntime.material_code,
                MSILDowntime.duration,
                MSILDowntime.reason_id,
                MSILDowntimeReasons.reason,
                MSILDowntimeReasons.reason_type
            ).filter(MSILDowntime.shop_id == shop_id)\
            .filter(MSILDowntime.start_time >= shift_start_time,MSILDowntime.start_time <= shift_end_time)\
            .join(MSILDowntime,MSILDowntime.material_code ==  MSILPart.material_code,isouter=True)\
            .join(MSILDowntimeReasons,MSILDowntime.reason_id == MSILDowntimeReasons.id,isouter=True)\
            .join(MSILEquipment,MSILDowntime.equipment_id ==  MSILEquipment.id,isouter=True)\
            .order_by(MSILDowntime.equipment_id,MSILDowntime.material_code,MSILDowntimeReasons.reason_type)\
            .all()
        return query

    def get_alerts_by_shop_id(self, shop_id, start_time, end_time):
        with self.session:
            query = (
                self.session.query(
                    AlertNotification.notification,
                    AlertNotification.created_at,
                    AlertNotification.alert_type,
                )
                .filter(AlertNotification.shop_id==shop_id,
                        AlertNotification.created_at  >= start_time,
                        AlertNotification.created_at <= end_time)\
                .distinct(AlertNotification.notification)  # Apply DISTINCT here
                .all()
            )
            
        return query
        
    def get_target_values_shop_id(self,shop_id):
        with self.session:
            query = self.session.query( 
                MSILEquipment.name,
                MSILEquipment.efficiency,
                MSILEquipment.efficiency,
                MSILEquipment.efficiency
            ).filter(MSILEquipment.shop_id==shop_id)\
            .all()

            return query
        
    def get_system_log_sheet_data(self,equipment_id,shop_id,shift_start_time,shift_end_time):
        with self.session:
            query = self.session.query(
                MSILEquipment.id.label('equipment_id'),
                MSILEquipment.name.label('equipment_name'),
                MSILBatch.id.label('batch_id'),
                MSILModel.model_name,
                MSILVariant.variant_name,
                MSILPart.pe_code,
                MSILPart.part_name,
                MSILBatch.prod_qty.label('quantity'),
                MSILQualityPunching.reject_qty,
                MSILQualityPunching.rework_qty,
                MSILQualityRemarks.remark,
                MSILInputMaterial.id.label('material_id'),
                MSILInputMaterial.details,
                MSILInputMaterial.thickness,
                MSILInputMaterial.width,
                MSILInputMaterial.material_qty,
                MSILBatch.start_time,
                MSILBatch.end_time,
                MSILQualityPunching.shop_id,
                MSILBatch.SPM,
                MSILBatch.material_code,
            ).filter(and_(MSILBatch.start_time >= shift_start_time,
                          MSILBatch.start_time < shift_end_time))\
            .join(MSILBatch,MSILBatch.material_code == MSILPart.material_code,isouter=True)\
            .join(MSILModel,MSILPart.model_id == MSILModel.id,isouter=True)\
            .join(MSILVariant,MSILPart.variant_id == MSILVariant.id,isouter=True)\
            .join(MSILQualityPunching,MSILQualityPunching.batch_id == MSILBatch.id,isouter=True)\
            .join(MSILQualityPunchingRecord,MSILQualityPunchingRecord.quality_punching_id ==  MSILQualityPunching.id,isouter=True)\
            .join(MSILInputMaterial,MSILInputMaterial.batch_id == MSILBatch.id,isouter=True)\
            .join(MSILEquipment,MSILEquipment.id == MSILQualityPunching.equipment_id)\
            .join(MSILQualityRemarks,MSILQualityRemarks.id == MSILQualityPunchingRecord.remark_id,isouter=True)\
            .filter(MSILQualityPunching.shop_id == shop_id)\
            .filter(MSILQualityPunching.equipment_id.in_(equipment_id))\
            .order_by(MSILQualityPunching.equipment_id,MSILBatch.id)\
            .all()

            return query
    
    def get_equipment_id_by_shop_id(self,shop_id):
        with self.session:
            query = self.session.query(
                MSILEquipment.id,
                MSILEquipment.name
            ).filter(MSILEquipment.shop_id==shop_id)\
            .all()

            equipment_id_arr = []
            equipment_arr = []
            for each in query:
                equipment_arr.append({
                    'id' : each.id,
                    'name' : each.name
                })
                equipment_id_arr.append(each.id)
            
            return equipment_id_arr,equipment_arr
            
            