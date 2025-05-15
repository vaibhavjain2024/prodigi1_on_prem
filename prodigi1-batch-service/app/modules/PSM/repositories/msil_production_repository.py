# from PSM.repositories.models.msil_machine_telemetry import MSILMachineTelemetry
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
from datetime import timedelta
ist_tz = pytz.timezone('Asia/Kolkata')

class MSILProductionRepository(Repository):
    """
    MSILProductionRepository to manage MSILMachine data table.
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILProduction
    
    def get_production(self, equipment_id, date, shift):
        with self.session:
            try:
                previous_production = self.session.query(self.model_type)\
                                                .filter(self.model_type.equipment_id == equipment_id)\
                                                .order_by(self.model_type.date)\
                                                .first()
                if previous_production is not None:
                    new_end_time = previous_production.date + timedelta(days=1) + timedelta(hours=6, minutes=30)
                    self.session.query(MSILBatch)\
                                .filter(MSILBatch.production_id == previous_production.id)\
                                .filter(MSILBatch.end_time == None)\
                                .update({MSILBatch.end_time : new_end_time}, synchronize_session=False)
                    self.session.commit()
                    print("mission succeeded")
                if previous_production is None:
                    print("mission not found")
            except Exception as e:
                # Handle the exception here, for example:
                print("An error occurred:", e)
                print("mission Failed")

            production = self.session.query(self.model_type) \
                               .filter(self.model_type.equipment_id == equipment_id) \
                               .filter(self.model_type.date == date) \
                               .first()
            if production == None:
                production = MSILProduction()
                production.equipment_id = equipment_id
                production.date = date
                production.shift = shift
                self.add(production)
            elif production.shift != shift:
                production.shift = shift
                self.session.merge(production)
                self.commit()
            return self.get(production.id)
    
    def change_variant(self, production_id, material_code, prev_material_code, part, shop_id):
        with self.session:
            production : MSILProduction = self.session.query(MSILProduction)\
                        .filter(MSILProduction.id == production_id).first()
            
            if production == None:
                raise Exception(f"Production with id {production_id} does not exist")
            
            if part == "part_2":
                production.part_2 = material_code
            else:
                production.part_1 = material_code
            self.session.merge(production)

            prev_plan = self.session.query(MSILPlan) \
                                    .filter(MSILPlan.material_code == prev_material_code) \
                                    .filter(MSILPlan.equipment_id == production.equipment_id) \
                                    .filter(MSILPlan.production_date == production.date) \
                                    .first()
            
            if prev_plan != None:
                prev_plan.status = PlanStatusEnum.PAUSED
                self.session.merge(prev_plan)
                self.session.commit()

            current_plan = self.session.query(MSILPlan) \
                                    .filter(MSILPlan.material_code == material_code) \
                                    .filter(MSILPlan.equipment_id == production.equipment_id) \
                                    .filter(MSILPlan.production_date == production.date) \
                                    .first()
            
            if current_plan != None:
                current_plan.status = PlanStatusEnum.RUNNING
                self.session.merge(current_plan)
                self.commit()


            batch = self.session.query(MSILBatch) \
                                .filter(MSILBatch.production_id == production_id) \
                                .filter(MSILBatch.material_code == prev_material_code) \
                                .filter(MSILBatch.end_time == None) \
                                .first()
            
            current_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)
            if batch == None:
                raise Exception(f"No current running batch found for {prev_material_code}!")
            batch.end_time = current_time
            new_batch = MSILBatch()
            new_batch.start_time = current_time
            new_batch.material_code = material_code
            new_batch.name = self.get_next_batch_name(batch.name, production, shop_id, batch.material_code, batch.prod_qty)
            new_batch.shift = production.shift
            new_batch.production_id = production_id
            new_batch.prod_qty = 0
            new_batch.output_id = "1"
            self.add(new_batch)

            quality = MSILQualityPunching()
            quality.material_code = material_code
            quality.batch_id = new_batch.id
            quality.shop_id = shop_id
            quality.equipment_id = production.equipment_id
            quality.hold_qty = 0
            self.add(quality)
    
    def update_downtime(self, production_id, is_down):
        with self.session:
            self.session.query(MSILProduction)\
                        .filter(MSILProduction.id == production_id) \
                        .update({MSILProduction.is_down : is_down})
            self.session.commit()
            
    def update_SPM_avg(self, production_id,part_1, part_2, SPM_update):
        with self.session:
            if part_1:
                self.session.query(MSILBatch) \
                            .filter(MSILBatch.production_id == production_id) \
                            .filter(MSILBatch.material_code == part_1) \
                            .update({MSILBatch.SPM : SPM_update})
            if part_2:
                self.session.query(MSILBatch) \
                        .filter(MSILBatch.production_id == production_id) \
                        .filter(MSILBatch.material_code == part_2) \
                        .update({MSILBatch.SPM : SPM_update})
            self.session.commit()

    def update_output(self, production_id,  material_code):
        with self.session:
            batch:MSILBatch = self.session.query(MSILBatch) \
                        .filter(MSILBatch.production_id == production_id) \
                        .filter(MSILBatch.material_code == material_code) \
                        .filter(MSILBatch.end_time == None) \
                        .first()
            if batch:
                if batch.output_id == None:
                    batch.output_id = "1"
                else:
                    batch.output_id = str(int(batch.output_id.split(",")[-1]) + 1)
                self.session.merge(batch)
                self.commit()
                        
        
    def start_production(self, production_id, input_parts, output_parts, work_order_number_1, work_order_number_2=None, with_input=True):
        current_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        with self.session:
            production : MSILProduction = self.get(production_id)
            if production.status == ProductionStatusEnum.RUNNING:
                raise Exception("Production is already in running state!")
            
            equipment : MSILEquipment = self.session.query(MSILEquipment) \
                                       .filter(MSILEquipment.id == production.equipment_id).first()
            machine_name = equipment.name
            part_1 : MSILPart= None
            model_1 : MSILModel = None
            part_1, model_1 = self.session.query(MSILPart, MSILModel) \
                                            .filter(MSILPart.material_code == output_parts[0]) \
                                            .join(MSILModel, MSILPart.model_id == MSILModel.id).first()
            part_2 : MSILPart= None
            model_2 : MSILModel = None
            if len(output_parts) > 1:
                part_2, model_2 = self.session.query(MSILPart, MSILModel) \
                                            .filter(MSILPart.material_code == output_parts[0]) \
                                            .join(MSILModel, MSILPart.model_id == MSILModel.id).first()
            
            if (work_order_number_1 == "NA"):
                #alert
                notification = f"{machine_name} {model_1.model_name} {part_1.part_name} is not planned, but production is on."
                self.production_without_plan_alert(notification, equipment.shop_id)
            else:
                 #update plan status
                plan = self.session.query(MSILPlan) \
                                   .filter(MSILPlan.work_order_number == work_order_number_1) \
                                   .filter(MSILPlan.material_code == part_1.material_code).first()
                if plan:
                    plan.status = PlanStatusEnum.RUNNING
                    self.session.merge(plan)
                    self.session.commit()
            
            if (work_order_number_2 == "NA"):
                notification = f"{machine_name} {model_2.model_name} {part_2.part_name} is not planned, but production is on."
                self.production_without_plan_alert(notification, equipment.shop_id)
            elif work_order_number_2 != None:
                #update plan status
                plan = self.session.query(MSILPlan) \
                                   .filter(MSILPlan.work_order_number == work_order_number_2) \
                                   .filter(MSILPlan.material_code == part_2.material_code).first()
                if plan:
                    plan.status = PlanStatusEnum.RUNNING
                    self.session.merge(plan)
                    self.session.commit()
            
            production.part_1 = output_parts[0]
            batch = MSILBatch()
            batch.start_time = current_time
            batch.name = "1:" + work_order_number_1
            batch.prod_qty = 0
            batch.shift = production.shift
            batch.material_code = output_parts[0]
            batch.production_id = production_id
            self.add(batch)

            quality = MSILQualityPunching()
            quality.material_code = output_parts[0]
            quality.batch_id = batch.id
            quality.shop_id = equipment.shop_id
            quality.equipment_id = production.equipment_id
            quality.hold_qty = 0
            self.add(quality)            

            if with_input:
                input_parts_first = input_parts[output_parts[0]]
                for parts in input_parts_first:
                    part_obj = MSILInputMaterial()
                    part_obj.batch_id = batch.id 
                    part_obj.details = parts["material_details"]
                    part_obj.part_name = parts["name"]
                    part_obj.production_id = production_id
                    part_obj.thickness = parts["thickness"]
                    part_obj.width = parts["width"]
                    part_obj.material_qty = parts["qty"]
                    self.add(part_obj)

            if len(output_parts) > 1:
                production.part_2 = output_parts[1]
                batch = MSILBatch()
                batch.start_time = current_time
                batch.name = "1:" + work_order_number_2
                batch.prod_qty = 0
                batch.shift = production.shift
                batch.material_code = output_parts[1]
                batch.production_id = production_id
                self.add(batch)
                quality = MSILQualityPunching()
                quality.material_code = output_parts[1]
                quality.batch_id = batch.id
                quality.shop_id = equipment.shop_id
                quality.equipment_id = production.equipment_id
                quality.hold_qty = 0
                self.add(quality)      
                if with_input:
                    input_parts_second = input_parts[output_parts[1]]
                    for parts in input_parts_second:
                        part_obj = MSILInputMaterial()
                        part_obj.batch_id = batch.id 
                        part_obj.details = parts["material_details"]
                        part_obj.part_name = parts["name"]
                        part_obj.production_id = production_id
                        part_obj.thickness = parts["thickness"]
                        part_obj.width = parts["width"]
                        part_obj.material_qty = parts["qty"]
                        self.add(part_obj)
            production.status = ProductionStatusEnum.RUNNING
            self.session.merge(production)
            self.commit()

    def get_next_batch_name(self, batch_name, production : MSILProduction, shop_id, material_code, prod_qty):
            batch_number = int(batch_name.split(":")[0])
            if prod_qty > 0:
                batch_number = batch_number + 1
            work_order = batch_name.split(":")[1]
            if work_order == "NA":
                plan = self.session.query(MSILPlan.work_order_number.label("work_order_number"),
                                       MSILPlan.material_code.label("output_part")) \
                                .filter(MSILPlan.material_code == material_code) \
                                .filter(MSILPlan.shop_id == shop_id) \
                                .filter(MSILPlan.production_date == production.date) \
                                .first()
                if plan:
                    return str(batch_number) + ":" + plan.work_order_number
            return str(batch_number) + ":" + work_order
        
    # def get_prod_qty(self, start_time, end_time, equipment_id, material_code ):
    #     query = self.session.query(func.sum(MSILMachineTelemetry.quantity).label("prod_qty")) \
    #                             .filter(MSILMachineTelemetry.timestamp >= start_time) \
    #                             .filter(MSILMachineTelemetry.timestamp <= end_time) \
    #                             .filter(MSILMachineTelemetry.equipment_id == equipment_id) \
    #                             .filter(MSILMachineTelemetry.material_code == material_code) \
    #                             .first()
    #     return query.prod_qty

        
    def production_without_plan_alert(self, notification, shop_id):
        notification_obj = AlertNotification()
        notification_obj.notification = notification
        notification_obj.notification_metadata = None
        notification_obj.alert_type = "Production without plan"
        notification_obj.created_at = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        notification_obj.shop_id = shop_id
        self.add(notification_obj)
        
    def update_program(self, production_id, current_time, output_parts, work_order_1, work_order_2, shop_id):
        with self.session:
            production : MSILProduction = self.get(production_id)
            if production.status == None:
                raise Exception("Production is not in running status")

            prev_part_1 = production.part_1
            prev_part_2 = production.part_2
            production.part_1 = output_parts[0]
            if len(output_parts) > 1:
                production.part_2 = output_parts[1]
            else:
                production.part_2 = None
            self.session.merge(production)
            self.commit()
            
            batches = self.session.query(MSILBatch) \
                                .filter(MSILBatch.production_id == production_id) \
                                .filter(MSILBatch.end_time == None) \
                                .all()
            updated_batches = []
            batches_to_be_deleted = []
            for batch in batches:
                ## merge batch with previous batch in case batch time is less than 10 minutes
                if (current_time - batch.start_time) < datetime.timedelta(minutes=10):
                    prev_batch = self.session.query(MSILBatch) \
                                    .filter(MSILBatch.production_id == production_id) \
                                    .filter(MSILBatch.material_code == batch.material_code) \
                                    .filter(MSILBatch.start_time < batch.start_time) \
                                    .order_by(desc(MSILBatch.start_time)) \
                                    .first()
                    if prev_batch:
                        prev_batch.end_time = current_time
                        prev_batch.prod_qty = prev_batch.prod_qty + batch.prod_qty
                        batches_to_be_deleted.append(batch.id)
                        self.session.query(MSILQualityPunching) \
                                    .filter(MSILQualityPunching.batch_id == prev_batch.id) \
                                    .update({MSILQualityPunching.hold_qty : MSILQualityPunching.hold_qty + batch.prod_qty})
                else:
                    batch.end_time = current_time
                updated_batches.append(batch.id)
            
            self.session.query(MSILQualityPunching) \
                        .filter(MSILQualityPunching.batch_id.in_(batches_to_be_deleted)) \
                        .delete()

            self.session.query(MSILBatch) \
                        .filter(MSILBatch.id.in_(batches_to_be_deleted)) \
                        .delete()

            equipment : MSILEquipment = self.session.query(MSILEquipment) \
                                       .filter(MSILEquipment.id == production.equipment_id).first()
            machine_name = equipment.name
            part_1 : MSILPart= None
            model_1 : MSILModel = None
            part_model = self.session.query(MSILPart, MSILModel) \
                                            .filter(MSILPart.material_code == production.part_1) \
                                            .join(MSILModel, MSILPart.model_id == MSILModel.id).first()
            if part_model:
                part_1 = part_model[0]
                model_1 = part_model[1]
            part_2 : MSILPart= None
            model_2 : MSILModel = None
            if len(output_parts) > 1:
                part_model_2 = self.session.query(MSILPart, MSILModel) \
                                            .filter(MSILPart.material_code == production.part_2) \
                                            .join(MSILModel, MSILPart.model_id == MSILModel.id).first()
                if part_model_2:
                    part_2 = part_model[0]
                    model_2 = part_model[1]

            prev_plan = self.session.query(MSILPlan) \
                    .filter(MSILPlan.material_code == prev_part_1) \
                    .filter(MSILPlan.equipment_id == production.equipment_id) \
                    .filter(MSILPlan.production_date == production.date) \
                    .first()
        
            if prev_plan != None:
                prev_plan.status = PlanStatusEnum.PAUSED
                self.session.merge(prev_plan)

            if prev_part_2:
                prev_plan = self.session.query(MSILPlan) \
                        .filter(MSILPlan.material_code == prev_part_2) \
                        .filter(MSILPlan.equipment_id == production.equipment_id) \
                        .filter(MSILPlan.production_date == production.date) \
                        .first()
            
                if prev_plan != None:
                    prev_plan.status = PlanStatusEnum.PAUSED
                    self.session.merge(prev_plan)
            
            if (work_order_1 == "NA"):
                #alert
                notification = f"{machine_name} {model_1.model_name} {part_1.part_name} is not planned, but production is on."
                self.production_without_plan_alert(notification, shop_id)
            else:
                 #update plan status
                plan = self.session.query(MSILPlan) \
                                   .filter(MSILPlan.work_order_number == work_order_1) \
                                   .filter(MSILPlan.material_code == part_1.material_code).first()
                if plan:
                    plan.status = PlanStatusEnum.RUNNING
                    self.session.merge(plan)
                    self.session.commit()
            
            if (work_order_2 == "NA"):
                notification = f"{machine_name} {model_2.model_name} {part_2.part_name} is not planned, but production is on."
                self.production_without_plan_alert(notification, shop_id)
            elif work_order_2 != None:
                #update plan status
                plan = self.session.query(MSILPlan) \
                                   .filter(MSILPlan.work_order_number == work_order_2) \
                                   .filter(MSILPlan.material_code == part_2.material_code).first()
                if plan:
                    plan.status = PlanStatusEnum.RUNNING
                    self.session.merge(plan)
                    self.session.commit()

            batch = MSILBatch()
            batch.start_time = current_time
            batch.name = "1:" + work_order_1
            batch.prod_qty = 0
            batch.shift = production.shift
            batch.material_code = output_parts[0]
            batch.production_id = production_id
            batch.output_id = "1"
            self.add(batch)

            quality = MSILQualityPunching()
            quality.material_code = output_parts[0]
            quality.batch_id = batch.id
            quality.shop_id = equipment.shop_id
            quality.equipment_id = production.equipment_id
            quality.hold_qty = 0
            self.add(quality)      

            if len(output_parts) > 1:
                production.part_2 = output_parts[1]
                batch = MSILBatch()
                batch.start_time = current_time
                batch.name = "1:" + work_order_2
                batch.prod_qty = 0
                batch.shift = production.shift
                batch.material_code = output_parts[1]
                batch.production_id = production_id
                batch.output_id = "1"
                self.add(batch)

                quality = MSILQualityPunching()
                quality.material_code = output_parts[1]
                quality.batch_id = batch.id
                quality.shop_id = equipment.shop_id
                quality.equipment_id = production.equipment_id
                quality.hold_qty = 0
                self.add(quality)

            return updated_batches, prev_part_1, prev_part_2

    def start_batch(self, production_id, current_time, shop_id, shift):
        batches_new  = []
        with self.session:
            production: MSILProduction = self.get(production_id)

            if production.status is None:
                raise Exception("Production is not in running status")

            if shop_id is None:
                equipment = self.session.query(MSILEquipment).filter_by(id=production.equipment_id).first()
                if not equipment:
                    raise Exception("Missing equipment with ID %d for production (shop_id is None)",
                                 production.equipment_id)

            batches = self.session.query(MSILBatch) \
                .filter(MSILBatch.production_id == production_id) \
                .filter(MSILBatch.end_time == None) \
                .all()

            for batch in batches:

                batch.end_time = current_time - timedelta(seconds=20)
                new_batch = MSILBatch()
                new_batch.start_time = current_time
                new_batch.material_code = batch.material_code
                new_batch.name = self.get_next_batch_name(batch.name, production, shop_id, batch.material_code, batch.prod_qty)
                new_batch.shift = shift if shift else production.shift
                new_batch.production_id = production_id
                new_batch.prod_qty = 0
                new_batch.output_id = "1"
                self.add(new_batch)

                quality = MSILQualityPunching()
                quality.material_code = batch.material_code
                quality.batch_id = new_batch.id
                quality.shop_id = shop_id if shop_id else equipment.shop_id
                quality.equipment_id = production.equipment_id
                quality.shift = shift
                quality.hold_qty = 0
                self.add(quality)

                if batch.prod_qty == 0:
                    self.session.query(MSILQualityPunching).filter(MSILQualityPunching.batch_id == batch.id).delete()
                    self.session.query(MSILBatch).filter(MSILBatch.id == batch.id).delete()
                    self.session.commit()
                else:
                     batches_new.append(batch.id)
        return batches_new, production.part_1, production.part_2
    # --------------------------------------------------------------------------------------------------------------
    #
    # event [
    #     {} API
    #     {} API
    # ]
    #
    # SQS - [batch_id : [1,2,3,4], timestamp, equipment, recepie]
    # base -> batch - join > quality_pucnging
    # punching - -----------equipment_id, material_code - ----> recepie
    #---------------------------------------------------------------------------------------------------------------------

    # def get_production_details(self, production_id , part_1 , part_2 = None):
    #     with self.session:
    #         prod_data = self.session.query(self.model_type,
    #                                        MSILModel.model_name,
    #                                        MSILPart.part_name,
    #                                        MSILPart.pe_code,
    #                                        MSILVariant.common_name,
    #                                        MSILQualityPunching.hold_qty,
    #                                        MSILQualityPunching.reject_qty,
    #                                        MSILQualityPunching.rework_qty,
    #                                        MSILBatch.prod_qty,
    #                                        MSILPlan.planned_quantity) \
    #                                 .join(MSILModel, MSILModel.id == self.model_type.equipment_id)



    #     machine = self.session.query(Machine).filter(Machine.id == machine_id).first()

    #     current_shift = session.query(Shift).filter(Shift.start_time <= production_date, Shift.end_time >= production_date).first()

    #     parts = session.query(Part).filter(Part.machine_id == machine_id, Part.production_date == production_date).all()

    #     part_details = []
    #     for part in parts:
    #         part_detail = {
    #             'Model': part.model_name,
    #             'Part Name': part.part_name,
    #             'PE Code': part.pe_code,
            
    #         }
    #         part_details.append(part_detail)

    #     batches = self.session.query(MSILBatch).filter(MSILBatch.id == machine_id, Batch.production_date == production_date).all()

    #     batch_details = []
    #     for batch in batches:
    #         batch_detail = {
    #             'Batch ID': batch.batch_id,
    #             'I/P Material Handling ID': batch.input_material_handling_id,
    #             'O/P Material Handling ID': batch.output_material_handling_id,
    #             'Start Time': batch.start_time,
    #             'End Time': batch.end_time,
    #             'Actual Quantity': batch.actual_quantity,
    #             'Reject/Rework': batch.reject_rework,
    #             # Add other batch details here
    #         }
    #         batch_details.append(batch_detail)

    #     # Return all collected data
    #     return {
    #         'Machine': machine.name,
    #         'Production Date': production_date,
    #         'Shift': current_shift.name,
    #         'Shift Downtime': current_shift.downtime,
    #         'Parts': part_details,
    #         'Batches': batch_details,
    #     }


    def pause_production(self, production_id):
        with self.session:
            production = self.session.query(MSILProduction).filter_by(id=production_id).first()

            if production:
                production.status = None
                production.part_1 = None
                production.part_2 = None

                batches = self.session.query(MSILBatch) \
                                .filter(MSILBatch.production_id == production_id) \
                                .filter(MSILBatch.end_time == None) \
                                .all()
                for batch in batches:
                    batch.end_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)  
                    if batch.prod_qty == 0:
                        input_materials = self.session.query(MSILInputMaterial).filter(MSILInputMaterial.batch_id == batch.id).all()
                        for input_material in input_materials:
                            self.session.delete(input_material)
                        self.session.query(MSILQualityPunching).filter(MSILQualityPunching.batch_id == batch.id).delete()
                        self.session.query(MSILBatch).filter(MSILBatch.id == batch.id).delete()
                self.session.commit() 
                return "Production paused successfully."
            else:
                raise ValueError("Production with the specified ID was not found.")
            
    def get_production_view(self,first_shift_time, prodution_id,shop_id):
        
        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)

        with self.session:
            production = self.session.query(MSILProduction).filter(MSILProduction.id==prodution_id).first()
            start = first_shift_time
            # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
            # start = start_query.shift_start_timing
            start_time = ist_tz.localize(datetime.datetime.combine(production.date,start)).replace(tzinfo=None)

            output =[production]
            part_list =[]

            breaks= self.session.query(MSILShopBreaks).filter(MSILShopBreaks.shop_id==shop_id, MSILShopBreaks.start_time<cur_datetime.time())
            break_duration = 0
            for item in breaks:
                if item.end_time> cur_datetime.time():
                    break_duration += (cur_datetime - datetime.datetime.combine(production.date, item.start_time)).total_seconds() / 60
                    # break_duration += (cur_datetime - ist_tz.localize(datetime.datetime.combine(production.date, item.start_time))).total_seconds() / 60

                    # break_duration += (cur_datetime.time()- item.start_time).total_seconds()/60
                else:
                    break_duration += item.duration_minutes
            
            runtime = (cur_datetime - start_time).total_seconds()/60
            runtime = runtime - break_duration

            if production.part_1:
                plan_quantity_1 = 0
                part_1 = self.session.query(MSILPart).filter(MSILPart.material_code==production.part_1).first()
                model_1 =  self.session.query(MSILModel).filter(MSILModel.id == part_1.model_id).first()
                # part_list.append(part_1)
                plan_1 = self.session.query(MSILPlan).filter(MSILPlan.material_code==production.part_1, MSILPlan.production_date==production.date).first()
                if plan_1:
                    plan_quantity_1 = plan_1.planned_quantity
                all_parts_1 = self.session.query(MSILPart, MSILVariant.common_name, MSILPart.material_code).join(MSILVariant, MSILPart.variant_id==MSILVariant.id, isouter=True).filter(MSILPart.part_name==part_1.part_name).filter(MSILPart.model_id==part_1.model_id)
                variant_set_1 = set()

                for item in all_parts_1:
                    if item[1]:
                        variant_set_1.add((item[1], item[2]))  # Use a tuple for uniqueness
                variant_list_1 = [{'name': name, 'material_code': material_code} for name, material_code in variant_set_1]
                # variant_set_1 = set()
                # for item in all_parts_1:
                #     if item[1]:
                #         variant_set_1.add((item[1],item[2]))
                # variant_list_1 = list(variant_set_1)

                input_subquery = self.session.query(MSILInputMaterial.batch_id.label('batch_id'), func.string_agg(MSILInputMaterial.details.cast(String),', ').label('details')).group_by(MSILInputMaterial.batch_id).subquery()
                batch_1 = self.session.query(MSILBatch, MSILBatch.SPM,func.coalesce(MSILBatch.prod_qty,0), func.coalesce(MSILQualityPunching.reject_qty,0), func.coalesce(MSILQualityPunching.rework_qty,0), func.coalesce(MSILQualityPunching.hold_qty,0), input_subquery.c.details) \
                .join(MSILQualityPunching, MSILBatch.id==MSILQualityPunching.batch_id, isouter=True) \
                .join(input_subquery, input_subquery.c.batch_id == MSILBatch.id , isouter=True) \
                .filter(MSILBatch.production_id==production.id,MSILBatch.material_code==production.part_1).order_by(desc(MSILBatch.start_time)).all()
                total_efficiency_1 = []
                batch_1_list = []
                duration_sum = 0
                weighted_sum = 0
                for batch in batch_1:
                    cur_batch : MSILBatch = batch[0]
                    batch_start = cur_batch.start_time
                    batch_end = cur_batch.end_time or cur_datetime
                    downtime_sum = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_1,start_time=batch_start,end_time=batch_end,reason_type='breakdown')
                    idle_sum = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_1,start_time=batch_start,end_time=batch_end,reason_type='idle')
                    batch_time = (batch_end - batch_start).total_seconds()/60
                    efficiency = (batch_time-downtime_sum)*100/(batch_time-idle_sum)
                    total_efficiency_1.append((batch_time,efficiency))
                    batch_1_list.append(tuple(batch) + (efficiency,))


                batch_sum_1 = sum(batch[2] for batch in batch_1)

                for item in total_efficiency_1:
                    weighted_sum += item[0]*item[1]
                    duration_sum += item[0]
                
                efficiency_1 = weighted_sum/duration_sum
                
                # idle_1 = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_1,start_time=start_time,end_time=cur_datetime,reason_type='idle')

                # downtime_1 = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_1,start_time=start_time,end_time=cur_datetime,reason_type='breakdown')
                
                # efficiency_1 = (runtime - float(downtime_1))*100/(runtime - float(idle_1))



                spm_1 = self.session.query(func.coalesce(MSILEquipment.SPM,0)).filter(MSILEquipment.id==production.equipment_id).scalar()

                hold_1= sum(item[5] for item in batch_1)
                rework_1 = sum(item[4] for item in batch_1)
                reject_1 = sum(item[3] for item in batch_1)

                part_list.append({
                    'part_obj':part_1,
                    'plan':plan_quantity_1,
                    'actual': batch_sum_1,
                    'variant_list': variant_list_1,
                    'batch_list': batch_1_list,
                    'reject':reject_1,
                    'rework':rework_1,
                    'hold':hold_1,
                    'efficiency':efficiency_1,
                    'spm':spm_1,
                    'model': model_1.model_name
                })

            if production.part_2:
                part_2 = self.session.query(MSILPart).filter(MSILPart.material_code==production.part_2).first()
                model_2 =  self.session.query(MSILModel).filter(MSILModel.id == part_2.model_id).first()
                plan_quantity_2 = 0
                plan_2 = self.session.query(MSILPlan).filter(MSILPlan.material_code==production.part_2, MSILPlan.production_date==production.date).first()
                if plan_2:
                    plan_quantity_2 = plan_2.planned_quantity
                all_parts_2 = self.session.query(MSILPart, MSILVariant.common_name, MSILPart.material_code).join(MSILVariant, MSILPart.variant_id==MSILVariant.id, isouter=True).filter(MSILPart.part_name==part_2.part_name).filter(MSILPart.model_id==part_2.model_id)
                # variant_set_2 = set()
                # for item in all_parts_2:
                #     if item[1]:
                #         variant_set_2.add((item[1],item[2]))
                # variant_list_2 = list(variant_set_2)
                variant_set_2 = set()

                for item in all_parts_2:
                    if item[1]:
                        variant_set_2.add((item[1], item[2]))  # Use a tuple for uniqueness
                variant_list_2 = [{'name': name, 'material_code': material_code} for name, material_code in variant_set_2]
                input_subquery = self.session.query(MSILInputMaterial.batch_id.label('batch_id'), func.string_agg(MSILInputMaterial.details.cast(String),', ').label('details')).group_by(MSILInputMaterial.batch_id).subquery()
                batch_2 = self.session.query(MSILBatch, MSILBatch.SPM,func.coalesce(MSILBatch.prod_qty,0), func.coalesce(MSILQualityPunching.reject_qty,0), func.coalesce(MSILQualityPunching.rework_qty,0), func.coalesce(MSILQualityPunching.hold_qty,0), input_subquery.c.details) \
                .join(MSILQualityPunching, MSILBatch.id==MSILQualityPunching.batch_id, isouter=True) \
                .join(input_subquery, input_subquery.c.batch_id == MSILBatch.id , isouter=True) \
                .filter(MSILBatch.production_id==production.id,MSILBatch.material_code==production.part_2).order_by(desc(MSILBatch.start_time)).all()
                batch_2_list = []
                total_efficiency_2 = []
                duration_sum = 0
                weighted_sum = 0
                for batch in batch_2:
                    cur_batch : MSILBatch = batch[0]
                    batch_start = cur_batch.start_time
                    batch_end = cur_batch.end_time or cur_datetime
                    downtime_sum = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_2,start_time=batch_start,end_time=batch_end,reason_type='breakdown')
                    idle_sum = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_2,start_time=batch_start,end_time=batch_end,reason_type='idle')
                    batch_time = (batch_end - batch_start).total_seconds()/60
                    efficiency = (batch_time-downtime_sum)*100/(batch_time-idle_sum)
                    total_efficiency_2.append((batch_time,efficiency))
                    batch_2_list.append(tuple(batch) + (efficiency,))
                    # print(f'idle:{idle_sum}, downtime:{downtime_sum}, batchtime:{batch_time}, start:{str(batch_start)}, end:{str(batch_end)}, efficiency:{efficiency}, id:{cur_batch.id}, eqp_id:{production.equipment_id}')
                
                batch_sum_2 = sum(batch[2] for batch in batch_2)

                for item in total_efficiency_2:
                    weighted_sum += item[0]*item[1]
                    duration_sum += item[0]
                
                efficiency_2 = weighted_sum/duration_sum
                
                # idle_2 = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_2,start_time=start_time,end_time=cur_datetime,reason_type='idle')

                # downtime_2 = self.downtime_duration(eqp_id=production.equipment_id,material_code=production.part_2,start_time=start_time,end_time=cur_datetime,reason_type='breakdown')
                
                # efficiency_2 = (runtime - float(downtime_2))*100/(runtime - float(idle_2))

                spm_2 = self.session.query(func.coalesce(MSILEquipment.SPM,0)).filter(MSILEquipment.id==production.equipment_id).scalar()

                hold_2= sum(item[5] for item in batch_2)
                rework_2 = sum(item[4] for item in batch_2)
                reject_2 = sum(item[3] for item in batch_2)

                part_list.append({
                    'part_obj':part_2,
                    'plan':plan_quantity_2,
                    'actual': batch_sum_2,
                    'variant_list': variant_list_2,
                    'batch_list': batch_2_list,
                    'reject':reject_2,
                    'rework':rework_2,
                    'hold':hold_2,
                    'efficiency':efficiency_2,
                    'spm':spm_2,
                    'model': model_2.model_name
                })
                
            output.append(part_list)

        return output
    
    def downtime_duration(self,eqp_id, material_code, start_time, end_time,reason_type):
        with self.session:
            downtime_tuple = self.session.query(
                MSILDowntime.start_time,MSILDowntime.end_time
            ).select_from(MSILDowntime).join(
                MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True).filter(
                MSILDowntimeReasons.reason_type==reason_type,
                or_(MSILDowntime.material_code==material_code,MSILDowntime.part_2_material_code==material_code),
                MSILDowntime.equipment_id == eqp_id,
                MSILDowntime.start_time<=end_time,
                or_(MSILDowntime.end_time.is_(None),MSILDowntime.end_time>=start_time)
                # MSILDowntime.start_time >= start_time,
                # or_(MSILDowntime.start_time <= end_time, MSILDowntime.end_time.is_(None))
            ).all()
            duration = 0
            for item in downtime_tuple:
                if item[0]<start_time:
                    item_start = start_time
                else:
                    item_start = item[0]
                if item[1]==None or item[1]>end_time:
                    item_end=end_time
                else:
                    item_end=item[1]
                
                duration += (item_end-item_start).total_seconds()/60

            return duration
    
    def get_current_parts_in_production(self,shop_id,production_date):
        with self.session:
            return self.session.query(func.count(self.model_type.part_1),func.count(self.model_type.part_2)) \
                                .join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id) \
                                .filter(MSILEquipment.shop_id == shop_id,
                                    self.model_type.date == production_date,
                                        self.model_type.status == ProductionStatusEnum.RUNNING).first()
        