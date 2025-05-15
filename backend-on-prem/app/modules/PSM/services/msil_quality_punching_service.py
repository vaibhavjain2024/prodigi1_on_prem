import datetime
from app.modules.PSM.repositories.models.msil_quality_punch_record import MSILQualityPunchingRecord
from app.modules.PSM.repositories.models.msil_quality_reason import MSILQualityReasons
from app.modules.PSM.repositories.models.msil_quality_remark import MSILQualityRemarks

from app.modules.PSM.repositories.models.msil_quality_updation import MSILQualityUpdation
from ..repositories.msil_equipment_repository import MSILEquipmentRepository
from ..repositories.msil_part_repository import MSILPartRepository
from ..repositories.msil_model_repository import MSILModelRepository
from ..repositories.models.msil_quality_punching import MSILQualityPunching
from ..repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
from ..repositories.msil_quality_updation_repository import MSILQualityUpdationRepository


import pytz

class MSILQualityPunchingService:
    def __init__(self, repository: MSILQualityPunchingRepository, eqp_repo:MSILEquipmentRepository, part_repo:MSILPartRepository, model_repo:MSILModelRepository, updation_repo:MSILQualityUpdationRepository):
        self.repository = repository
        self.equipment_repository = eqp_repo
        self.part_repository = part_repo
        self.model_repository = model_repo 
        self.update_repository = updation_repo 


    def get_quality_part_filters(self, shop_id):
        filters = self.repository.get_unique_quality_filters(shop_id)
        return self.transform_filters(filters)
    
    def get_quality_punching(self,punching_id):
        quality_obj = self.repository.get_quality_with_time(punching_id)
        quality : MSILQualityPunching = quality_obj[0]
        prod_qty = quality_obj[2]

        qp = self.repository.get_punching_by_id(punching_id) 

        return { 
                    "records" : self.transform_punching_records(qp),
                    "metrics" : {
                        "prod_qty" : prod_qty,
                        "hold_qty" : quality.hold_qty or 0,
                        "reject_qty" : quality.reject_qty or 0,
                        "rework_qty" : quality.rework_qty or 0,
                        "ok_qty" : quality.ok_qty or 0
                    } 
                }

    def get_reasons(self, shop_id):
        return self.repository.get_reasons(shop_id)
    
    def update_punching(self, quality_id, punching_list, username):

        rework_qty = 0
        reject_qty = 0
        quality : MSILQualityPunching = None
        quality_obj = self.repository.get_quality_with_time(quality_id)
        quality = quality_obj[0]
        batch_time = quality_obj[1]
        prod_qty = quality_obj[2]

        now_time = datetime.datetime.now()

        if quality.status == "SUBMITTED":
            raise Exception("Quality punching is already submitted")

        ### Time validation
        if (now_time - batch_time).days > 4:
            raise Exception("Quality punching cannot be updated one day past 4 day of production")

        for punching in punching_list:

            is_deleted = punching.get("is_deleted", None)
            if is_deleted:
                continue

            quantity = punching["quantity"]
            evaluation = punching["evaluation"]

            if quantity > prod_qty:
                raise Exception("Quantity cannot be more than production quantity")
            if evaluation == "REJECT":
                reject_qty = reject_qty + quantity
            elif evaluation == "REWORK":
                rework_qty = rework_qty + quantity
            elif evaluation == "":
                pass
            else:
                raise Exception("Unknown evaluation")

        ### UPDATE PUNCHING
        if prod_qty < (reject_qty + rework_qty):
            raise Exception("Total of reject and rework quantity cannot be higher than hold quantity")
        self.repository.update_quantity(quality_id=quality_id,reject=reject_qty,rework=rework_qty, prod_qty=prod_qty)

        ### UPDATE RECORDS ###
        for punching in punching_list:
            punching_id = punching.get("id",None)
            is_deleted = punching.get("is_deleted", None)
            is_updated = punching.get("is_updated", None)

            if is_deleted:
                if punching_id == None:
                    raise Exception("Quality punching record id cannot be null for to be deleted record")
                self.repository.delete_punching_record(punching_id, username, now_time)
                continue
            
            quantity = punching["quantity"]
            evaluation = punching["evaluation"]
            reason_id = punching["reason_id"]
            remark = punching["remark"]

            if evaluation == "":
                pass
            elif punching_id == None:
                self.repository.punch_quality(quality_id, quantity, evaluation, reason_id, remark, username, now_time)
            elif is_updated:
                self.repository.punch_quality(quality_id, quantity, evaluation, reason_id, remark, username, now_time, punching_id)

            

    def submit_punching(self, punching_id, username):
        now_time = datetime.datetime.now()
        quality : MSILQualityPunching = self.repository.get(punching_id)
        if (quality.rework_qty != None) and (quality.rework_qty > 0):
            rework = MSILQualityUpdation()
            rework.quality_punching_id = quality.id
            rework.rework_qty = quality.rework_qty
            rework.pending_rework_qty = rework.rework_qty
            rework.status = "Pending"
            rework = self.update_repository.add(rework)
        self.repository.submit_quality(punching_id,username, now_time)
        

    def get_quality(self, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None, shift = None,
                            batch = None, hold_qty_filter = None, page_no=1, page_size=10):
        
        if machine_list == [] or machine_list == "ALL":
            machine_list = None
        
        if model_list == [] or model_list == "ALL":
            model_list = None
        
        if part_name_list == [] or part_name_list == "ALL":
            part_name_list = None

        if start_time == [] or start_time == "ALL":
            start_time = None

        if end_time == [] or end_time == "ALL":
            end_time = None

        if shift == [] or shift == "ALL":
            shift = None

        if batch == [] or batch == "ALL":
            batch = None

        if hold_qty_filter == [] or hold_qty_filter == "ALL":
            hold_qty_filter = None
        
        quality = self.repository.get_quality(shop_id, machine_list =machine_list,
                   model_list = model_list, part_name_list = part_name_list, 
                   batch = batch, hold_qty_filter = hold_qty_filter, start_time = start_time, end_time = end_time,
                   shift = shift, limit=page_size, offset=(page_no-1)*page_size)
        
        quality_list = []
        for qt in quality:
            quality_list.append({
                "id": qt.id,
                "machine" : qt.machine_name,
                "model" : qt.model_name,
                "part_name" : qt.part_name,
                "start_time": qt.start_time,
                "end_time" : qt.end_time,
                "batch_id" : qt.batch,
                "hold_qty" : qt.hold_qty,
                "reject_qty" : qt.reject_qty,
                "rework_qty" : qt.rework_qty,
                "prod_qty" : qt.prod_qty,
                "ok_qty" : qt.ok_qty,
                "shift" : qt.shift,
                "status" : qt.status,
                "submitted_by" : qt.submitted_by,
                "submitted_at" : qt.submitted_at
            })
        
        return quality_list
    
    def transform_filters(self,filters):
        filter_list = []
        for filter in filters:
            filter_list.append({
                "machine_group" : filter[0],
                "machine" : filter[1],
                "model" : filter[2],
                "part_name" : filter[3],
                "Batch" :  filter[4]
                
            })
        return filter_list
    
    def transform_punching_records(self, qp ):
        qp_list = []

        for punch in qp:
            quality_punching_record : MSILQualityPunchingRecord = punch[0]
            reason : MSILQualityReasons= punch[1]
            remark : MSILQualityRemarks = punch[2]
            qp_list.append({
                "id" : quality_punching_record.id,
                "quantity" : quality_punching_record.quantity,
                "evaluation" : quality_punching_record.evaluation.name,
                "quality_punching_id" : quality_punching_record.quality_punching_id,
                "remark" : remark.remark,
                "reason" : reason.reason,
                "reason_id" : reason.id,
                "created_by" : quality_punching_record.created_by,
                "created_at" : quality_punching_record.created_at,
                "updated_by" : quality_punching_record.updated_by,
                "updated_at" : quality_punching_record.updated_at
            })

        return qp_list
    
    def get_quality_punching_report(self,csvwriter, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None, shift = None,
                            batch = None, hold_qty_filter = None):
        
        if machine_list == [] or machine_list == "ALL":
            machine_list = None
        
        if model_list == [] or model_list == "ALL":
            model_list = None
        
        if part_name_list == [] or part_name_list == "ALL":
            part_name_list = None

        if start_time == [] or start_time == "ALL":
            start_time = None

        if end_time == [] or end_time == "ALL":
            end_time = None

        if shift == [] or shift == "ALL":
            shift = None

        if batch == [] or batch == "ALL":
            batch = None

        if hold_qty_filter == [] or hold_qty_filter == "ALL":
            hold_qty_filter = None
        
        quality = self.repository.get_quality(shop_id, machine_list =machine_list,
                   model_list = model_list, part_name_list = part_name_list, 
                   batch = batch, hold_qty_filter = hold_qty_filter, start_time = start_time, end_time = end_time,
                   shift = shift, limit=1000)
        
        print("Quality-----")
        print(quality)
        
        
        fields = [ 'Machine', 'Model', 'Part Name', 'Start Time', 'End Time','BatchID', 'Hold Qty','Shift' ]
        quality_list = []
        rows = []
        csvwriter.writerow(fields)

        for qt in quality:
            quality_list.append({
                "machine" : qt.machine_name,
                "model" : qt.model_name,
                "part_name" : qt.part_name,
                "start_time": qt.start_time.strftime("%d-%m-%y | %I:%M:%S %p"),
                "end_time" : qt.end_time.strftime("%d-%m-%y | %I:%M:%S %p"),
                "batch_id" : qt.batch,
                "hold_qty" : qt.hold_qty,
                "shift" : qt.shift
            })
            
        
        return quality_list
        # for qt_item in quality_list:
        #     fields = list(qt_item.values())
        #     csvwriter.writerow(fields)
        #     rows.append(fields)
        # return rows
        