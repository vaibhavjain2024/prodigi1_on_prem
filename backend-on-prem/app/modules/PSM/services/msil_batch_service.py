# services/batch_service.py
from ..repositories.msil_batch_repository import MSILBatchRepository
from ..services.msil_production_service import MSILProductionService
from ..repositories.models.msil_equipment import MSILEquipment
from ..repositories.models.msil_production import MSILProduction
from ..repositories.models.msil_batch import MSILBatch
from datetime import datetime,timedelta
import datetime as dt 
from ..repositories.models.msil_quality_punching import MSILQualityPunching
import pytz
# from logger_common import get_logger
# logger = get_logger()

ist_tz = pytz.timezone('Asia/Kolkata')


class MSILBatchService:
    def __init__(self, repository: MSILBatchRepository):
        self.repository = repository

    def get_shift_for_new_batch_current_hour(self, current_time):

        """Calculate the next shift based on the current hour for New batch creation.
        Expected value for hour will be 6, 15, 0"""

    def get_shift(self,downtime_datetime : dt.datetime):
        downtime_datetime = downtime_datetime.replace(microsecond=0)
        shift_start = None
        SHIFT_MAPPING_WITH_TIME = {
        (dt.time(6, 30, 0), dt.time(15, 14, 59)) : "A",
        (dt.time(15, 15, 0), dt.time(23, 59, 59)) : "B",
        (dt.time(0, 0, 0), dt.time(6, 29, 59)) : "C"
        }
        
        for each_shift in SHIFT_MAPPING_WITH_TIME:
            if each_shift[0] <= downtime_datetime.time() <= each_shift[1]:
                shift = SHIFT_MAPPING_WITH_TIME.get(each_shift)
                shift_start = each_shift[0]
                shift_end = each_shift[1]
                break
        return shift, shift_start, shift_end

    def update_batches_without_end_time(self, msil_production_service):
        current_time = datetime.now(ist_tz).replace(tzinfo=None) - timedelta(minutes=30)  # Set the end time to current timestamp
        shift,shift_start,shift_end = self.get_shift(current_time)
        date = (datetime.now(ist_tz)- timedelta(minutes=30)).date() 
        shift_start = datetime.combine(date=date,time=shift_start)
        shift_end = datetime.combine(date=date,time=shift_end)
        # logger.info("shift_start = " + str(shift_start) + ", shift_end = " + str(shift_end))
        unfinished_batches = self.repository.get_batches_with_null_end_time(shift_start=shift_start,shift_end=shift_end)
        for row in unfinished_batches:
            print(
                    f"ID: {row.id}, Name: {row.name}, Shift: {row.shift}, Start Time: {row.start_time}, "
                    f"End Time: {row.end_time}, Prod Qty: {row.prod_qty}, Input ID: {row.input_id}, "
                    f"Output ID: {row.output_id}, Production ID: {row.production_id}, Material Code: {row.material_code}, "
                    f"SPM: {row.SPM}, Equipment ID: {row.equipment_id}, Shop ID: {row.shop_id}"
                )
        # logger.info("total number of unclosed batches : %d", len(unfinished_batches))
        current_time=shift_end + timedelta(seconds = 20)
        # print(shift_end)

        if not unfinished_batches:
            # logger.info("No unfinished batches found.")
            return

        # logger.info("current Date time : %s", {current_time})
        change_time_epoch = int(current_time.timestamp())
        next_shift_time = datetime.now(ist_tz).replace(tzinfo=None) + timedelta(minutes=30) 
        next_shift,shift_start,shift_end = self.get_shift(next_shift_time)

        # logger.info("Shift  : %s", {shift})

        for batch in unfinished_batches:
            production_id = batch.production_id
            # shop_id = self.repository.get_shop_id(production_id)
            try:
                msil_production_service.start_batch(production_id, current_time, shift=next_shift)
            except Exception as e:
                # logger.error(f"Error starting batch for production ID {production_id}: {e}")
                pass

    def batch_closure_job(self):
        current_shift,shift_start,shift_end  =  self.get_shift(shift_time)
        unfinished_batches = self.repository.get_batches_with_null_end_time()
        max_id = self.repository.get_max_of_batch_id()

        if not unfinished_batches:
            # logger.info("No unfinished batches found.")
            return
        
        current_time = datetime.now(ist_tz).replace(tzinfo=None)  # Set the end time to current timestamp
        shift_time = current_time + timedelta(hours=1)
        current_shift,shift_start,shift_end  =  self.get_shift(shift_time)
        new_quality =[]
        print("found batches",len(unfinished_batches))
        for batch in unfinished_batches:
            batch_name = batch.name
            new_name = batch_name
            try:
                new_name =str(int(batch_name.split(':')[0])+1) +":"+ (batch_name.split(':')[1]) 
            except Exception as e :
                pass
                # logger.error("broken in renaming the batch")

            self.repository.update_unfinished_batches(batch.id,current_time)

            new_batch = MSILBatch()
            new_batch.start_time = current_time
            new_batch.name = new_name
            new_batch.prod_qty = 0
            new_batch.input_id = batch.input_id,
            new_batch.output_id = batch.output_id,
            new_batch.shift = current_shift
            new_batch.material_code = batch.material_code
            new_batch.production_id = batch.production_id
            new_batch.SPM = batch.SPM 
            self.repository.add(new_batch)           


            new_quality.append(MSILQualityPunching(
                material_code = new_batch.material_code,
                batch_id = new_batch.id,
                shop_id = batch.shop_id,
                equipment_id = batch.equipment_id,
                hold_qty = 0
            ))
        
        self.repository.bulk_insert_batches(batch_arr=new_quality)

    def get_batch_with_details(self, batch_id):

        batch_details = self.repository.get_batches_with_input_materials(batch_id)
        if not batch_details:
            raise ValueError(f"No batch/Input material found with ID: {batch_id}")

        # batch, input_material = batch_details
        batch = batch_details[0][0]  # Batch details will be the first element of each tuple
        input_materials = [detail[1] for detail in batch_details]  # Input materials will be the second element

        # Initialize empty fields for Input1 and Input2
        input1_material_batch_details = ""
        input2_material_batch_details = ""
        input1_quantity = "0.000"
        input2_quantity = "0.000"

        # Handle input material 1 if it exists
        if len(input_materials) > 0:
            input1_material = input_materials[0]
            input1_material_batch_details = input1_material.details if input1_material else ""
            input1_quantity = f"{input1_material.material_qty:.3f}" if input1_material else "0.000"

        # Handle input material 2 if it exists
        if len(input_materials) > 1:
            input2_material = input_materials[1]
            input2_material_batch_details = input2_material.details if input2_material else ""
            input2_quantity = f"{input2_material.material_qty:.3f}" if input2_material else "0.000"

        # Construct the input_material list to return
        input_material_list = []
        for i, material in enumerate(input_materials):
            input_material_list.append({
                "id": material.id,
                "part_name": material.part_name,
                "details": material.details,
                "thickness": material.thickness,
                "width": material.width,
                "material_qty": material.material_qty,
            })

        return {
            "batch": {
                "id": batch.id,
                "name": batch.name,
                "shift": batch.shift,
                "start_time": batch.start_time,
                "end_time": batch.end_time,
                "prod_qty": batch.prod_qty,
                "input_id": batch.input_id,
                "output_id": batch.output_id,
                "material_code": batch.material_code,
                "SPM": batch.SPM,
            },
            "input_material": input_material_list,
            "Input1_material_batch_details": input1_material_batch_details,
            "Input2_material_batch_details": input2_material_batch_details,
            "input1_quantity": input1_quantity,
            "input2_quantity": input2_quantity,
        }