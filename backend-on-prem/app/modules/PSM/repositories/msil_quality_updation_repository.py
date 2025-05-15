from app.modules.PSM.repositories.models.msil_model import MSILModel
from app.modules.PSM.repositories.models.msil_quality_updation import MSILQualityUpdation
from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from app.modules.PSM.repositories.models.msil_quality_updation_record import MSILQualityUpdationRecord
from app.modules.PSM.repositories.models.msil_quality_updation_reason import MSILQualityUpdationReasons
from app.modules.PSM.repositories.models.msil_quality_updation_remarks import MSILQualityUpdationRemarks
from .repository import Repository
from .models.msil_part import MSILPart
from .models.msil_equipment import MSILEquipment
from .models.msil_quality_updation_reason import MSILQualityUpdationReasons
from .models.msil_part import MSILPart
from .models.msil_batch import MSILBatch
from sqlalchemy.orm import Session
from collections import defaultdict
from sqlalchemy import (
    and_,
    desc,
    func,
    case
)
from sqlalchemy.sql.expression import true

class MSILQualityUpdationRepository(Repository):
    """
    MSILQualityUpdationRepository to manage MSILQualityUpdation data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILQualityUpdation


    def get_unique_quality_updation_filters(self, shop_id):
        with self.session:      
            
            query = (
                    self.session.query(
                        MSILEquipment.equipment_group, MSILEquipment.name,
                                    MSILModel.model_name, MSILPart.part_name,
                                    MSILBatch.id
                                    ) \
                                .select_from(self.model_type) \
                                .join(MSILModel, self.model_type.model_id == MSILModel.id) \
                                .join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id) \
                                .join(MSILBatch, self.model_type.batch_id == MSILBatch.id) \
                                .join(MSILPart, self.model_type.material_code == MSILPart.material_code) \
                                .filter(self.model_type.shop_id == shop_id) 
                                )
            
            return query.distinct().all()

    
    def get_updation(self, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None,batch = None, status = None, shift = None,
                            limit=10, offset=0):
        """Get updation from db 
        Default sort : By start time

        Returns:
            model_list: list of models
        """ 
        with self.session:       
            query = self.session.query(self.model_type.id.label("id"),
                                       MSILEquipment.name.label("machine_name"),
                                       MSILModel.model_name.label("model_name"),
                                       MSILPart.part_name.label("part_name"), 
                                       MSILBatch.start_time.label("start_time"),
                                       MSILBatch.end_time.label("end_time"), 
                                       MSILBatch.name.label("batch"),
                                       MSILBatch.prod_qty.label("prod_qty"), 
                                       self.model_type.rework_qty.label("rework_qty"),
                                       self.model_type.pending_rework_qty.label("pending_rework_qty"),
                                       self.model_type.reject_qty.label("reject_qty"),
                                       self.model_type.recycle_qty.label("recycle_qty"),
                                       self.model_type.ok_qty.label("ok_qty"),
                                       MSILBatch.shift.label("shift"),
                                       self.model_type.status.label("status"),
                                       MSILQualityPunching.id.label("quality_id"),
                                       MSILQualityPunching.submitted_by.label("submitted_by"),
                                       MSILQualityPunching.submitted_at.label("submitted_at")) \
                                .select_from(self.model_type) 
                                

            if(status):
                query = query.filter(self.model_type.status == status)                

            query = query.join(MSILQualityPunching, self.model_type.quality_punching_id == MSILQualityPunching.id)
            
            query = query.filter(MSILQualityPunching.shop_id == shop_id)

            query = query.join(MSILBatch, MSILQualityPunching.batch_id == MSILBatch.id)

            if(batch):
                query = query.filter(MSILBatch.name == batch)

            if(start_time):
                query = query.filter(MSILBatch.start_time>=(start_time))  

            if(end_time):
                query = query.filter(MSILBatch.end_time<=(end_time))   

            if(shift):
                query = query.filter(MSILBatch.shift.in_(shift))

            query = query.join(MSILPart, MSILQualityPunching.material_code == MSILPart.material_code) 

            query = query.join(MSILModel, MSILPart.model_id == MSILModel.id)
            
            if(model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))
                        

            if(part_name_list):
                query = query.filter(MSILPart.part_name.in_(part_name_list))   

            query = query.join(MSILEquipment, MSILQualityPunching.equipment_id == MSILEquipment.id) 
            
            if(machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))
            
            return query.order_by(desc(MSILBatch.start_time)) \
                    .limit(limit) \
                    .offset(offset)\
                    .all()

    def get_updation_by_id(self, updation_id):
        with self.session:
            return self.session.query(MSILQualityUpdationRecord, MSILQualityUpdationReasons, MSILQualityUpdationRemarks) \
                                .filter(MSILQualityUpdationRecord.quality_updation_id == updation_id) \
                                .filter(MSILQualityUpdationRecord.is_deleted != true()) \
                                .join(MSILQualityUpdationRemarks, MSILQualityUpdationRecord.remark_id == MSILQualityUpdationRemarks.id) \
                                .join(MSILQualityUpdationReasons, MSILQualityUpdationRemarks.reason_id == MSILQualityUpdationReasons.id) \
                                .all()

    def get_quality_with_time(self, quality_id):
        with self.session:
            return self.session.query(self.model_type, MSILBatch.start_time) \
                               .filter(self.model_type.id == quality_id) \
                               .join(MSILQualityPunching, MSILQualityPunching.id == self.model_type.quality_punching_id) \
                               .join(MSILBatch, MSILBatch.id == MSILQualityPunching.batch_id) \
                               .first()

    def delete_updation_record(self, updation_id, username, current_time):
        with self.session:
            punch = self.session.query(MSILQualityUpdationRecord) \
                                .filter(MSILQualityUpdationRecord.id == updation_id) \
                                .first()
            punch.is_deleted = True
            punch.updated_by = username
            punch.updated_at = current_time
            self.commit()
            return

    def update_quantity(self, quality_id, rework_qty=None, recycle=None, reject=None, ok_qty=None):
        with self.session:
            quality_obj : MSILQualityUpdation = self.session.query(self.model_type).get(quality_id)
            quality_obj.reject_qty = reject
            quality_obj.pending_rework_qty = rework_qty - (reject + recycle + ok_qty)
            quality_obj.recycle_qty = recycle
            quality_obj.ok_qty = ok_qty
            self.commit()

    def update_quality(self, quality_id, quantity, evaluation, reason_id, remark, username, current_time, updation_id=None):
        with self.session:
            remark_obj = MSILQualityUpdationRemarks()
            remark_obj.remark = remark
            remark_obj.reason_id = reason_id
            self.add(remark_obj)
            updation : MSILQualityUpdationRecord = None
            if updation_id == None:
                updation = MSILQualityUpdationRecord()
                updation.created_by = username
                updation.created_at = current_time
                updation.quality_updation_id = quality_id
                updation.quantity = quantity
                updation.evaluation = evaluation
                updation.remark_id = remark_obj.id
                updation.is_deleted = False
                self.add(updation)
                return
            else:
                updation = self.session.query(MSILQualityUpdationRecord) \
                                    .get(updation_id)
                
                updation.quality_updation_id = quality_id
                updation.quantity = quantity
                updation.evaluation = evaluation
                updation.remark_id = remark_obj.id
                updation.is_deleted = False
                updation.updated_by = username
                updation.updated_at = current_time
                self.commit()

    def submit_quality(self, quality_id, username):
        with self.session:
            quality_obj = self.session.query(self.model_type).get(quality_id)
            quality_obj.status="SUBMITTED"
            quality_obj.submitted_by=username
            self.commit()
        

    def get_reasons(self, shop_id):
        with self.session:
            results = self.session.query(MSILQualityUpdationReasons.id, MSILQualityUpdationReasons.reason, MSILQualityUpdationReasons.type) \
                .filter(MSILQualityUpdationReasons.shop_id == shop_id,MSILQualityUpdationReasons.is_deleted==False) \
                .all()
            
        grouped_reasons = defaultdict(list)
        for result in results:
            _, reason, reason_type = result
            formatted_reason_type = reason_type.name  # Convert enum value to name
            grouped_reasons[formatted_reason_type].append({result.id: reason})
        return dict(grouped_reasons)
        
        
