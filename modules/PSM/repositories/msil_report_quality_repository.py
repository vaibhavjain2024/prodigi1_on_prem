from modules.PSM.repositories.models.msil_quality_updation_remarks import MSILQualityUpdationRemarks
from modules.PSM.repositories.models.msil_quality_updation_reason import MSILQualityUpdationReasons, ReworkEvaluationTypeEnum
from modules.PSM.repositories.models.msil_model import MSILModel
from modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from modules.PSM.repositories.models.msil_quality_updation import MSILQualityUpdation
from modules.PSM.repositories.models.msil_quality_punch_record import MSILQualityPunchingRecord
from modules.PSM.repositories.models.msil_quality_reason import MSILQualityReasons, QualityEvaluationTypeEnum
from modules.PSM.repositories.models.msil_quality_remark import MSILQualityRemarks
from .repository import Repository
from .models.msil_part import MSILPart
from .models.msil_equipment import MSILEquipment
from .models.msil_production import MSILProduction
from .models.msil_part import MSILPart
from .models.msil_recipe import MSILRecipe
from .models.msil_batch import MSILBatch
from .models.msil_quality_updation_record import MSILQualityUpdationRecord
from .models.msil_variant import MSILVariant
from collections import defaultdict
from sqlalchemy.orm import Session
import datetime
from sqlalchemy import (
    and_,
    desc,
    func,
    case
)
from sqlalchemy.sql.expression import true


class MSILReportQualityRepository(Repository):
    """
    MSILPartRepository to manage MSILPart data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILQualityPunching
        self.part_model = MSILPart
        # self.record_model = MSILQualityPunchingRecord

    def get_unique_report_filters(self, shop_id):
        with self.session:         
            output_subquery = self.get_part_equipment(shop_id)
            
            return self.session.query(output_subquery.c.equipment_group, output_subquery.c.equipment_name,
                                    MSILModel.model_name, self.part_model.part_name, 
                                    ) \
                                .join(MSILModel, self.part_model.model_id == MSILModel.id) \
                                .join(output_subquery, self.part_model.material_code == output_subquery.c.material_code) \
                                .filter(MSILModel.shop_id==shop_id) \
                                .distinct().all()
        
    def get_part_equipment(self, shop_id):

        with self.session:
            output_1_subquery = \
                self.session.query(MSILRecipe.equipment_id.label('equipment_id'),
                                    MSILRecipe.output_1.label('material_code')) \
                            .join(MSILPart, MSILRecipe.output_1==MSILPart.material_code) 
                            
            
            output_2_subquery = \
                self.session.query(MSILRecipe.equipment_id.label('equipment_id'),
                                    MSILRecipe.output_2.label('material_code')) \
                            .join(MSILPart, MSILRecipe.output_2==MSILPart.material_code)
            
            combined = output_1_subquery.union_all(output_2_subquery).subquery()

            equipment_query = self.session.query(combined.c.material_code.label('material_code'), 
                                                 MSILEquipment.id.label('equipment_id'), 
                                                 MSILEquipment.name.label('equipment_name'), 
                                                 MSILEquipment.equipment_group.label('equipment_group')) \
                                          .join(MSILEquipment, combined.c.equipment_id==MSILEquipment.id) \
                                          .filter(MSILEquipment.shop_id == shop_id) \
                                          .subquery()

            return equipment_query
    

    def get_machine_quality_data(self, shop_id, start_date, end_date,machine_list = None,
                                 model_list=None, part_name_list = None, shift = None):
        equipment_data = defaultdict(list)

        number_of_days = (end_date - start_date).days + 1

        def date_range(start_date, end_date):
            
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += datetime.timedelta(days=1)
            return date_list
        days = date_range(start_date , end_date)
        
        with self.session:
            query = self.session.query(
                    MSILEquipment.name.label("Equipment_Name"),
                    MSILBatch.shift.label("Shift"),
                    func.coalesce(func.sum(MSILQualityPunching.hold_qty)/number_of_days,0).label("hold_qty"),
                    func.coalesce(func.sum(MSILQualityPunching.reject_qty + (func.coalesce(MSILQualityUpdation.reject_qty,0)))/number_of_days,0).label("reject_qty"),
                    func.coalesce(func.sum(MSILQualityUpdation.pending_rework_qty)/number_of_days,0).label("pending_rework_qty"),
                    func.coalesce(func.sum(func.coalesce(MSILQualityUpdation.recycle_qty,0))/number_of_days,0).label("recycle_qty"),
                    func.coalesce(
                        func.sum( 
                            func.coalesce(MSILQualityUpdation.ok_qty,0) 
                                + MSILQualityPunching.ok_qty
                            )/number_of_days
                            ,0).label("ok_qty")
                ) \
                .select_from(self.model_type) \
                .join(MSILEquipment , self.model_type.equipment_id == MSILEquipment.id) \
                .join(MSILBatch, self.model_type.batch_id == MSILBatch.id) \
                .join(MSILProduction , MSILBatch.production_id == MSILProduction.id) \
                .join(MSILQualityUpdation, MSILQualityUpdation.quality_punching_id == MSILQualityPunching.id, isouter=True) \
                .filter(MSILQualityPunching.shop_id == shop_id ) \
                .filter(MSILProduction.date.in_(days)) \
                
            if(shift):
                query = query.filter(MSILBatch.shift.in_(shift))
                
            query = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code) 

            query = query.join(MSILModel, MSILPart.model_id == MSILModel.id)
            
            if(model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))
                        
            if(part_name_list):
                query = query.filter(MSILPart.part_name.in_(part_name_list))   
            
            if(machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))
                
            results = query \
                .group_by(MSILEquipment.name, MSILBatch.shift) \
                .subquery()
                        

            reasons = self.get_quality_reasons(shop_id,number_of_days, days,machine_list = None,
                                 model_list=None, part_name_list = None, shift = None)

            query = self.session.query( results.c.Equipment_Name,
                                         results.c.Shift,
                                         func.coalesce(results.c.hold_qty,0),
                                         func.coalesce(results.c.reject_qty),
                                         func.coalesce(results.c.pending_rework_qty),
                                         func.coalesce(results.c.recycle_qty),
                                         func.coalesce(results.c.ok_qty),
                                         func.coalesce(reasons.c.Reject_reasons),
                                         func.coalesce(reasons.c.Reject_count),
                                         func.coalesce(reasons.c.Reject_quantity,0)
            ) \
            .select_from(results) \
            .join(reasons, and_(results.c.Equipment_Name == reasons.c.Reject_Equipment_Name, reasons.c.Reject_Shifts == results.c.Shift), isouter=True) \
            .all()


            for result in query:
                equipment_name = result[0]
                shift = result[1]
                shift_key = f"Shift {shift}"
                if equipment_name not in equipment_data:
                    equipment_data[equipment_name] = {
                        "machine_name": equipment_name,
                        # "Shifts": {}
                    }
                if shift_key not in equipment_data[equipment_name]:
                    equipment_data[equipment_name][shift_key] = {
                        "name": shift_key,
                        "hold_qty": round(float(result[2]), 2),
                        "reject_qty": round(float(result[3]), 2),
                        "pending_rework_qty": round(float(result[4]), 2),
                        "recycle_qty": round(float(result[5]), 2),
                        "ok_qty": round(float(result[6]), 2),
                        "reasons": [],
                    }

                if result[7] is not None:
                    equipment_data[equipment_name][shift_key]["reasons"].append(
                        {
                            "reason": result[7],
                            "count": round(float(result[8]), 2),
                            "quantity": round(float(result[9]), 2),
                        }
                    )
            output = list(equipment_data.values())
            return output
        
           
    def get_quality_reasons(self,shop_id,number_of_days,days,machine_list = None,
                                 model_list=None, part_name_list = None, shift = None):
        with self.session:
            
            query = (
                self.session.query(
                    func.coalesce(func.count(MSILQualityPunchingRecord.id)/number_of_days,0).label("Punching_Count"),
                    func.coalesce(func.sum(MSILQualityPunchingRecord.quantity)/number_of_days,0).label("Puching_quantity"),
                    MSILEquipment.name.label("Equipment_Name"),
                    MSILBatch.shift.label("Punching_Shift"), MSILQualityReasons.reason.label("Punching_reason") 
                )
                .select_from(MSILQualityPunchingRecord) \
                .join(MSILQualityPunching, MSILQualityPunching.id == MSILQualityPunchingRecord.quality_punching_id) \
                .join(MSILEquipment , self.model_type.equipment_id == MSILEquipment.id) \
                .join(MSILBatch, self.model_type.batch_id == MSILBatch.id) \
                .join(MSILProduction , MSILBatch.production_id == MSILProduction.id) \
                .join(MSILQualityRemarks, MSILQualityPunchingRecord.remark_id == MSILQualityRemarks.id) \
                .join(MSILQualityReasons, MSILQualityRemarks.reason_id == MSILQualityReasons.id) \
                .filter(MSILQualityPunching.shop_id == shop_id ) \
                .filter(MSILProduction.date.in_(days)) \
                .filter(MSILQualityReasons.type == QualityEvaluationTypeEnum.REJECT)) \
            
            if(shift):
                query = query.filter(MSILBatch.shift.in_(shift))
                
            query = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code) 

            query = query.join(MSILModel, MSILPart.model_id == MSILModel.id)
            
            if(model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))
                    
            if(part_name_list):
                query = query.filter(MSILPart.part_name.in_(part_name_list))   
            
            if(machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))

            results_punching = query \
                .group_by(MSILEquipment.name, MSILBatch.shift, MSILQualityReasons.reason) \
                .subquery()
            
            query = (
                self.session.query(
                    func.coalesce(func.count(MSILQualityUpdationRecord.id)/number_of_days).label("Updation_Count"),
                    func.coalesce(func.sum(MSILQualityUpdationRecord.quantity)/number_of_days,0).label("Updation_quantity"),
                    MSILEquipment.name.label("Equipment_Name"),
                    MSILBatch.shift.label("Updation_Shift"), MSILQualityUpdationReasons.reason.label("Updation_reason") 
                )
                .select_from(MSILQualityUpdationRecord) \
                .join(MSILQualityUpdation, MSILQualityUpdation.id == MSILQualityUpdationRecord.quality_updation_id) \
                .join(MSILQualityPunching, MSILQualityUpdation.quality_punching_id == MSILQualityPunching.id) \
                .join(MSILEquipment , self.model_type.equipment_id == MSILEquipment.id) \
                .join(MSILBatch, self.model_type.batch_id == MSILBatch.id) \
                .join(MSILProduction , MSILBatch.production_id == MSILProduction.id) \
                .join(MSILQualityUpdationRemarks, MSILQualityUpdationRecord.remark_id == MSILQualityUpdationRemarks.id) \
                .join(MSILQualityUpdationReasons, MSILQualityUpdationRemarks.reason_id == MSILQualityUpdationReasons.id) \
                .filter(MSILQualityPunching.shop_id == shop_id ) \
                .filter(MSILProduction.date.in_(days)) \
                .filter(MSILQualityUpdationReasons.type == ReworkEvaluationTypeEnum.REJECT)) \
            
            if(shift):
                query = query.filter(MSILBatch.shift.in_(shift))
                
            query = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code) 

            query = query.join(MSILModel, MSILPart.model_id == MSILModel.id)
            
            if(model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))
                    
            if(part_name_list):
                query = query.filter(MSILPart.part_name.in_(part_name_list))   
            
            if(machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))

            results_rework = query \
                .group_by(MSILEquipment.name, MSILBatch.shift, MSILQualityUpdationReasons.reason) \
                .subquery()

            reasons = self.session.query((func.coalesce(results_punching.c.Equipment_Name,results_rework.c.Equipment_Name).label("Reject_Equipment_Name")),
                                         (func.coalesce(results_punching.c.Punching_Shift,results_rework.c.Updation_Shift).label("Reject_Shifts")),
                                         (func.coalesce(results_punching.c.Punching_reason,results_rework.c.Updation_reason).label("Reject_reasons")),
                                         ((func.coalesce(results_punching.c.Punching_Count,0) + func.coalesce(results_rework.c.Updation_Count,0)).label("Reject_count")),
                                         ((func.coalesce(results_punching.c.Puching_quantity,0) + func.coalesce(results_rework.c.Updation_quantity,0)).label("Reject_quantity"))
                                         ) \
                                .select_from(results_punching) \
                                .join(results_rework, and_(results_punching.c.Equipment_Name==results_rework.c.Equipment_Name ,
                                      results_punching.c.Punching_Shift==results_rework.c.Updation_Shift ,
                                      results_punching.c.Punching_reason==results_rework.c.Updation_reason), full=True) \
                                .subquery()
            
            return reasons
            