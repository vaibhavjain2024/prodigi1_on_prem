import datetime
from ..repositories.msil_equipment_repository import MSILEquipmentRepository
from ..repositories.msil_part_repository import MSILPartRepository
from ..repositories.msil_model_repository import MSILModelRepository
from ..repositories.models.msil_quality_punching import MSILQualityPunching
from ..repositories.models.msil_batch import MSILBatch
from ..repositories.models.msil_quality_updation_record import MSILQualityUpdationRecord
from ..repositories.models.msil_quality_updation_reason import MSILQualityUpdationReasons
from ..repositories.models.msil_quality_updation_remarks import MSILQualityUpdationRemarks

from ..repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
from ..repositories.models.msil_quality_updation import MSILQualityUpdation

import pytz

class MSILQualityUpdationService:
    def __init__(self, repository: MSILQualityUpdationRepository,
                  eqp_repo:MSILEquipmentRepository, 
                  part_repo:MSILPartRepository, 
                  model_repo:MSILModelRepository):
        self.repository = repository
        self.equipment_repository = eqp_repo
        self.part_repository = part_repo
        self.model_repository = model_repo  


    def get_quality_updation_part_filters(self, shop_id):
        
        
        filters = self.repository.get_unique_quality_updation_filters(shop_id)
        return self.transform_filters(filters)
    
    def get_quality_updation(self, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None, shift = None,
                            batch = None, status = None, page_no=1, page_size=10):
        
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

        if status == [] or status == "ALL":
            status = None
        
        quality = self.repository.get_updation(shop_id, machine_list =machine_list,
                   model_list = model_list, part_name_list = part_name_list, 
                   batch = batch, status = status, start_time = start_time, end_time = end_time,
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
                "prod_qty" : qt.prod_qty,
                "rework_qty" : qt.rework_qty,
                "pending_rework_qty" : qt.pending_rework_qty,
                "reject_qty" : qt.reject_qty,
                "recycle_qty" : qt.recycle_qty,
                "ok_qty" : qt.ok_qty,
                "status" : qt.status,
                "shift" : qt.shift,
                "quality_id" : qt.quality_id,
                "submitted_at" : qt.submitted_at,
                "submitted_by" : qt.submitted_by
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
        
    
    def get_quality_updation_report(self,csvwriter, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None, shift = None,
                            batch = None, status = None):
        
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

        if status == [] or status == "ALL":
            status = None
        
        quality = self.repository.get_updation(shop_id, machine_list =machine_list,
                   model_list = model_list, part_name_list = part_name_list, 
                   start_time = start_time, end_time = end_time,
                   shift = shift, batch = batch, status=status, limit=1000)
        
        # fields = [ 'Machine', 'Model', 'Part Name', 'Shift', 'Start Time', 'End Time', 'BatchID', 'Prod. Qty', 'Rework Qty' ,'Pending Rework Qty','Status' ]
        # rows = []
        # csvwriter.writerow(fields)

        quality_list = []

        for qt in quality:
            quality_list.append({
                "machine" : qt.machine_name,
                "model" : qt.model_name,
                "part_name" : qt.part_name,
                "shift" : qt.shift,
                "start_time": qt.start_time.strftime("%d-%m-%y | %I:%M:%S %p"),
                "end_time" : qt.end_time.strftime("%d-%m-%y | %I:%M:%S %p"),
                "batch_id" : qt.batch,
                "prod_qty" : qt.prod_qty,
                "rework_qty" : qt.rework_qty,
                "pending_rework_qty" : qt.pending_rework_qty,
                "status" : qt.status
    
            })
        
        return quality_list
            
        
        # for qt_item in quality_list:
        #     fields = list(qt_item.values())
        #     csvwriter.writerow(fields)
        #     rows.append(fields)
        # return rows
    

    def get_total_rework_qty(self, shop_id,machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None,end_time=None,
                            shift = None,batch = None, status = None
                            ):
        
        now = datetime.datetime.now()
        
        filters = (machine_list,model_list,part_name_list,start_time,end_time,shift,batch,status)
        if all(i is None for i in filters):
            start_time = datetime.datetime.combine(now.date(), datetime.time(0,0))
            end_time = datetime.datetime.combine(now.date(), datetime.time(23, 59, 59))

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

        if status == [] or status == "ALL":
            status = None
        
        quality = self.repository.get_updation(shop_id, machine_list =machine_list,
                   model_list = model_list, part_name_list = part_name_list,
                   batch=batch,status=status ,start_time = start_time, end_time = end_time, 
                   shift = shift, limit=1000)
        
        total_pending_rework_qty =0
        total_rework_qty = 0
        for qt in quality:
            if qt[8] != None:
                total_rework_qty+=qt[8]
            if qt[9] != None:
                total_pending_rework_qty+=qt[9]
        return {
            "total_rework_Qty" : total_rework_qty,
            "total_pending_rework_qty" : total_pending_rework_qty
                }


    def get_reasons(self, shop_id):
        return self.repository.get_reasons(shop_id)
        
            # if isinstance(qt, int):
            #     total_rework_qty += qt
            # elif isinstance(qt, tuple) and len(qt) > 0:
            #     model: MSILQualityUpdation = qt[0]
            #     total_rework_qty = total_rework_qty+ model.rework_qty
       
        
        # for qt in quality:
        #     model: MSILQualityUpdation = qt[0]
        #     total_rework_qty += model.rework_qty

    def get_quality_punching(self,punching_id):
        qp = self.repository.get_updation_by_id(punching_id) 
        updation : MSILQualityUpdation = self.repository.get(punching_id)
        return { 
                "records" : self.transform_updation_records(qp),
                "metrics" : {
                    "rework_qty" : updation.rework_qty,
                    "reject_qty" : updation.reject_qty,
                    "pending_rework_qty" : updation.pending_rework_qty,
                    "recycle_qty" : updation.recycle_qty,
                    "ok_qty" : updation.ok_qty
                } 
            }
    
    def transform_updation_records(self, qp ):
        qp_list = []

        for punch in qp:
            quality_updation_record : MSILQualityUpdationRecord = punch[0]
            reason : MSILQualityUpdationReasons= punch[1]
            remark : MSILQualityUpdationRemarks = punch[2]
            qp_list.append({
                "id" : quality_updation_record.id,
                "quantity" : quality_updation_record.quantity,
                "evaluation" : quality_updation_record.evaluation.name,
                "quality_punching_id" : quality_updation_record.quality_updation_id,
                "remark" : remark.remark,
                "reason" : reason.reason,
                "reason_id" : reason.id,
                "created_by" : quality_updation_record.created_by,
                "created_at" : quality_updation_record.created_at,
                "updated_by" : quality_updation_record.updated_by,
                "updated_at" : quality_updation_record.updated_at
            })

        return qp_list
    
    def submit_punching(self, punching_id, username):
        self.repository.submit_quality(punching_id,username)

    def update_updation(self, quality_id, updation_list, username):
        
        recycle_qty = 0
        reject_qty = 0
        ok_qty = 0
        quality : MSILQualityPunching = None
        # quality , batch_time = self.repository.get_quality_with_time(quality_id)
        quality_obj = self.repository.get_quality_with_time(quality_id)
        quality = quality_obj[0]
        batch_time = quality_obj[1]

        now_time = datetime.datetime.now()

        if quality.status == "SUBMITTED":
            raise Exception("Quality punching is already submitted")

        ### Time validation
        if (now_time - batch_time).days > 4:
            raise Exception("Quality punching cannot be updated 4 day past two days of production")

        for updation in updation_list:

            is_deleted = updation.get("is_deleted", None)
            if is_deleted:
                continue

            quantity = updation["quantity"]
            evaluation = updation["evaluation"]

            if quantity > quality.rework_qty:
                raise Exception("Quantity cannot be more than rework quantity")
            if evaluation == "REJECT":
                reject_qty = reject_qty + quantity
            elif evaluation == "RECYCLE":
                recycle_qty = recycle_qty + quantity
            elif evaluation == "OK":
                ok_qty = ok_qty + quantity
            else:
                raise Exception("Unknown evaluation")

        ### UPDATE PUNCHING
        if quality.rework_qty < (reject_qty + recycle_qty + ok_qty):
            raise Exception("Total of reject and rework quantity cannot be higher than hold quantity")
        self.repository.update_quantity(quality_id=quality_id,rework_qty=quality.rework_qty,reject=reject_qty,recycle=recycle_qty, ok_qty=ok_qty)

        ### UPDATE RECORDS ###
        for updation in updation_list:
            updation_id = updation.get("id",None)
            is_deleted = updation.get("is_deleted", None)
            is_updated = updation.get("is_updated", None)

            if is_deleted:
                if updation_id == None:
                    raise Exception("Quality punching record id cannot be null for to be deleted record")
                self.repository.delete_updation_record(updation_id, username, now_time)
                continue
            
            quantity = updation["quantity"]
            evaluation = updation["evaluation"]
            reason_id = updation["reason_id"]
            remark = updation["remark"]

            if updation_id == None:
                self.repository.update_quality(quality_id, quantity, evaluation, reason_id, remark, username, now_time)
            elif is_updated:
                self.repository.update_quality(quality_id, quantity, evaluation, reason_id, remark, username, now_time, updation_id)