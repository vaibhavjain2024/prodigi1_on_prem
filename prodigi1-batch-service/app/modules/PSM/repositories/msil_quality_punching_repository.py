from app.modules.PSM.repositories.models.msil_model import MSILModel
from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from app.modules.PSM.repositories.models.msil_quality_punch_record import MSILQualityPunchingRecord
from app.modules.PSM.repositories.models.msil_quality_reason import MSILQualityReasons
from app.modules.PSM.repositories.models.msil_quality_remark import MSILQualityRemarks
from .repository import Repository
from .models.msil_part import MSILPart
from .models.msil_equipment import MSILEquipment
from .models.msil_part import MSILPart
from .models.msil_batch import MSILBatch
from .models.msil_variant import MSILVariant
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case
)
from sqlalchemy.sql.expression import true


class MSILQualityPunchingRepository(Repository):
    """
    MSILPartRepository to manage MSILPart data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILQualityPunching
        # self.record_model = MSILQualityPunchingRecord

    def get_unique_quality_filters(self, shop_id):
        with self.session:      
            
            query = (
                    self.session.query(
                        MSILEquipment.equipment_group, MSILEquipment.name,
                                    MSILModel.model_name, MSILPart.part_name,
                                    MSILBatch.name
                                    ) \
                                .select_from(self.model_type) \
                                .filter(self.model_type.shop_id == shop_id) 
                                .join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id) \
                                .join(MSILBatch, self.model_type.batch_id == MSILBatch.id) \
                                .join(MSILPart, self.model_type.material_code == MSILPart.material_code) \
                                .join(MSILModel, MSILPart.model_id == MSILModel.id) \
                                )
            
            return query.distinct().all()
    
    def get_quality(self, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None,batch = None, hold_qty_filter = None, shift = None,
                            limit=10, offset=0):
        """Get quality from db 
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
                                        self.model_type.hold_qty.label("hold_qty"), 
                                        self.model_type.reject_qty.label("reject_qty"),
                                        self.model_type.rework_qty.label("rework_qty"),
                                        self.model_type.ok_qty.label("ok_qty"),
                                        MSILBatch.shift.label("shift"),
                                        self.model_type.status.label("status"),
                                        self.model_type.submitted_by.label("submitted_by"),
                                        self.model_type.submitted_at.label("submitted_at"),
                                        MSILBatch.prod_qty.label("prod_qty")) \
                                .select_from(self.model_type) \
                                .filter(self.model_type.shop_id == shop_id)

            if(hold_qty_filter != None):
                if(hold_qty_filter == 0):
                    query = query.filter(self.model_type.hold_qty == 0)
                else:
                    query = query.filter(self.model_type.hold_qty > 0)

            query = query.join(MSILBatch, self.model_type.batch_id == MSILBatch.id)

            if(batch):
                query = query.filter(MSILBatch.name == batch)

            if(start_time):
                query = query.filter(MSILBatch.start_time>=(start_time))  

            if(end_time):
                query = query.filter(MSILBatch.end_time<=(end_time))   

            if(shift):
                query = query.filter(MSILBatch.shift.in_(shift))
                
            query = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code) 


            query = query.join(MSILModel, MSILPart.model_id == MSILModel.id)
            
            if(model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))
                        

            if(part_name_list):
                query = query.filter(MSILPart.part_name.in_(part_name_list))   

            query = query.join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id) 
            
            if(machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))
            
            return query.order_by(desc(MSILBatch.start_time)) \
                    .limit(limit) \
                    .offset(offset)\
                    .all()
        
    def get_punching_by_id(self, punching_id):
        with self.session:
            return self.session.query(MSILQualityPunchingRecord, MSILQualityReasons, MSILQualityRemarks) \
                                .filter(MSILQualityPunchingRecord.quality_punching_id == punching_id) \
                                .filter(MSILQualityPunchingRecord.is_deleted != true()) \
                                .join(MSILQualityRemarks, MSILQualityPunchingRecord.remark_id == MSILQualityRemarks.id) \
                                .join(MSILQualityReasons, MSILQualityRemarks.reason_id == MSILQualityReasons.id) \
                                .all()
    
    # def get_reasons(self, shop_id):
    #     with self.session:
    #         return self.session.query(MSILQualityReasons.id, MSILQualityReasons.reason , MSILQualityReasons.type) \
    #                            .filter(MSILQualityReasons.shop_id == shop_id) \
    #                            .all()
        
    # def get_reasons(self, shop_id):
    #     with self.session:
    #         results = self.session.query(MSILQualityReasons.id, MSILQualityReasons.reason, MSILQualityReasons.type) \
    #         .filter(MSILQualityReasons.shop_id == shop_id) \
    #         .all()
        
    #     formatted_results = []
        
    #     for result in results:
    #         id, reason, reason_type = result
    #         formatted_reason_type = reason_type.name # Convert enum value to name
    #         formatted_results.append(( reason, formatted_reason_type))
        
    #     return formatted_results
    

    def get_reasons(self, shop_id):
        with self.session:
            results = self.session.query(MSILQualityReasons.id, MSILQualityReasons.reason, MSILQualityReasons.type) \
                .filter(MSILQualityReasons.shop_id == shop_id,MSILQualityReasons.is_deleted==False) \
                .all()
            
        grouped_reasons = defaultdict(list)
        for result in results:
            id, reason, reason_type = result
            formatted_reason_type = reason_type.name  # Convert enum value to name
            grouped_reasons[formatted_reason_type].append({id: reason})
        
        return dict(grouped_reasons)


    def get_quality_with_time(self, quality_id):
        with self.session:
            return self.session.query(self.model_type, MSILBatch.start_time, MSILBatch.prod_qty) \
                               .filter(self.model_type.id == quality_id) \
                               .join(MSILBatch, MSILBatch.id == self.model_type.batch_id) \
                               .first()

    def delete_punching_record(self, punching_id, username, current_time):
        with self.session:
            punch = self.session.query(MSILQualityPunchingRecord) \
                                .filter(MSILQualityPunchingRecord.id == punching_id) \
                                .first()
            punch.is_deleted = True
            punch.updated_by = username
            punch.updated_at = current_time
            self.commit()
            return
    
    def update_quantity(self, quality_id, rework=None, reject=None, prod_qty=None):
        with self.session:
            quality_obj : MSILQualityPunching = self.session.query(self.model_type).get(quality_id)
            quality_obj.hold_qty = prod_qty - (reject + rework) 
            quality_obj.reject_qty = reject
            quality_obj.rework_qty = rework
            self.commit()
    
    def submit_quality(self, quality_id, username, current_time):
        with self.session:
            quality_obj : MSILQualityPunching = self.session.query(self.model_type).get(quality_id)
            quality_obj.ok_qty = quality_obj.hold_qty
            quality_obj.hold_qty = 0
            quality_obj.status="SUBMITTED"
            quality_obj.submitted_by=username
            quality_obj.submitted_at = current_time
            self.commit()

    def punch_quality(self, quality_id, quantity, evaluation, reason_id, remark, username, current_time, punching_id=None):
        with self.session:
            remark_obj = MSILQualityRemarks()
            remark_obj.remark = remark
            remark_obj.reason_id = reason_id
            self.add(remark_obj)
            punch : MSILQualityPunchingRecord = None
            if punching_id == None:
                punch = MSILQualityPunchingRecord()
                punch.created_by = username
                punch.created_at = current_time
                punch.quality_punching_id = quality_id
                punch.quantity = quantity
                punch.evaluation = evaluation
                punch.remark_id = remark_obj.id
                punch.is_deleted = False
                self.add(punch)
                return
            else:
                punch = self.session.query(MSILQualityPunchingRecord) \
                                    .get(punching_id)
                
                punch.quality_punching_id = quality_id
                punch.quantity = quantity
                punch.evaluation = evaluation
                punch.remark_id = remark_obj.id
                punch.is_deleted = False
                punch.updated_by = username
                punch.updated_at = current_time
                self.commit()


    # def submit_punching(self, quality_id):
                
    def get_unique_parts_completed_count(self,start_time,end_time,shop_id):
        with self.session:       
            grouped_query = self.session.query(self.model_type.equipment_id.label("equipment_id"),
                                       self.model_type.material_code.label("material_code")) \
                                       .join(MSILBatch, self.model_type.batch_id == MSILBatch.id) \
                                .filter(self.model_type.shop_id == shop_id) \
                                .filter(MSILBatch.start_time >= start_time,MSILBatch.end_time<=end_time) \
                                .group_by(self.model_type.equipment_id,self.model_type.material_code)
            unique_completed_parts_count = self.session.query(func.count()).select_from(grouped_query.subquery()).scalar()
            return unique_completed_parts_count




    