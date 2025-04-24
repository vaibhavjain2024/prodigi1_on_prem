import datetime
from modules.PSM.repositories.models.msil_downtime_reason import MSILDowntimeReasons

from modules.PSM.repositories.models.msil_part import MSILPart
from modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.repositories.models.msil_downtime import MSILDowntime
import pytz
from modules.PSM.services.shift_util import get_shift, get_production_date
# from logger_common import get_logger
# logger = get_logger()


ist_tz = pytz.timezone('Asia/Kolkata')


class MSILDowntimeService:
    def __init__(self, repository: MSILDowntimeRepository, remark_repo: MSILDowntimeRemarkRepository,
                 reason_repo: MSILDowntimeReasonRepository, eqp_repo: MSILEquipmentRepository,
                 part_repo: MSILPartRepository, model_repo: MSILModelRepository, shift_repo: MSILShiftRepository):
        self.repository = repository
        self.reason_repository = reason_repo
        self.remark_repository = remark_repo
        self.equipment_repository = eqp_repo
        self.part_repository = part_repo
        self.model_repository = model_repo
        self.shift_repository = shift_repo

    def get_shift(self,downtime_datetime : datetime.datetime):
        downtime_datetime = downtime_datetime.replace(microsecond=0)
        shift_start = None
        SHIFT_MAPPING_WITH_TIME = {
        (datetime.time(6, 30, 0), datetime.time(15, 14, 59)) : "A",
        (datetime.time(15, 15, 0), datetime.time(23, 59, 59)) : "B",
        (datetime.time(0, 0, 0), datetime.time(6, 29, 59)) : "C"
        }
        
        for each_shift in SHIFT_MAPPING_WITH_TIME:
            if each_shift[0] <= downtime_datetime.time() <= each_shift[1]:
                shift = SHIFT_MAPPING_WITH_TIME.get(each_shift)
                shift_start = each_shift[0]
                shift_end = each_shift[1]
                break
        return shift, shift_start, shift_end
    
    def get_downtimes(self, shop_id, machine_list=None,
                      model_list=None, part_name_list=None,
                      start_time=None, end_time=None, start=None, end=None, shift=None,
                      reason=None, remarks=None, page_no=1, page_size=10):

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

        if remarks == [] or remarks == "ALL":
            remarks = None

        if reason == [] or reason == "ALL":
            reason = None

        downtimes = self.repository.get_remarks(shop_id, machine_list=machine_list,
                                                model_list=model_list, part_name_list=part_name_list,
                                                reason=reason, remarks=remarks, start_time=start_time,
                                                end_time=end_time, start=start, end=end,
                                                shift=shift, limit=page_size, offset=(page_no - 1) * page_size)

        downtime_dict = []
        for dt in downtimes:
            downtime_dict.append(self.model_to_dict(dt))

        return downtime_dict

    def get_total_duration(self, shop_id, machine_list=None,
                           model_list=None, part_name_list=None,
                           start_time=None, end_time=None, start=None, end=None, shift=None,
                           reason=None, remarks=None):

        # now = datetime.datetime.now()
        ist_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.datetime.now(ist_tz).replace(tzinfo=None)

        filters = (machine_list, model_list, part_name_list, start_time, end_time, start, end, shift, reason, remarks)

        if all(i is None for i in filters):
            start_time = datetime.datetime.combine(now.date(), datetime.time(0, 0))
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

        if remarks == [] or remarks == "ALL":
            remarks = None

        if reason == [] or reason == "ALL":
            reason = None

        downtimes = self.repository.get_remarks(shop_id, machine_list=machine_list,
                                                model_list=model_list, part_name_list=part_name_list, start=start,
                                                end=end,
                                                reason=reason, remarks=remarks, start_time=start_time,
                                                end_time=end_time,
                                                shift=shift, limit=1000)

        # downtime_dict = []
        # total_duration = 0
        # for dt in downtimes:
        #     # downtime_dict.append(self.model_to_dict(dt))
        #     model: MSILDowntime = dt[0]
        #     total_duration += model.duration

        # return total_duration
        total_duration = 0
        for dt in downtimes:
            # model: MSILDowntime = dt[0]

            duration = dt[6] if dt[6] is not None else 0

            total_duration += duration

        seconds = float(total_duration) * 60
        minutes = seconds // 60
        remaining_seconds = (seconds % 60) / 100.0
        downtime_duration = minutes + round(remaining_seconds, 2)
        total_duration = "{:.2f}".format(downtime_duration)

        return round(float(total_duration), 2)

        # total_duration = 0
        # for dt in downtimes:
        #     # downtime_dict.append(self.model_to_dict(dt))
        #     model: MSILDowntime = dt[0]
        #     if model.duration is not None:  # Check for null duration
        #         total_duration += model.duration
        #     elif model.start_time is not None and model.end_time is not None:  # Calculate duration for rows with valid start_time and end_time
        #         total_duration += (model.end_time - model.start_time).total_seconds()

        # return total_duration

    def start_downtime(self, shop_id, equipment_id, tag, output_1, output_2=None):
        prev_downtimes = self.repository.filter_by_many(shop_id=shop_id, equipment_id=equipment_id, end_time=None)
        reason: MSILDowntimeReasons = self.reason_repository.filter_by(shop_id=shop_id, tag=tag)

        reason_id = None
        reason_type = None
        if reason:
            reason_id = reason.id
            reason_type = reason.reason_type
        else:
            print("couldn't find tag so assigning")
            reason_id = 1
            reason_type = "idle"
            print(f"Reason not found for tag {tag}")
        self.equipment_repository.update_status(equipment_id, reason_type, shop_id)
        if prev_downtimes == []:
            downtime = MSILDowntime()
            downtime.start_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)
            downtime.reason_id = reason_id
            downtime.equipment_id = equipment_id
            downtime.material_code = output_1
            downtime.part_2_material_code = output_2
            downtime.shop_id = shop_id
            part_1: MSILPart = self.part_repository.filter_by(material_code=output_1)
            if part_1:
                downtime.model_id = part_1.model_id
            downtime.shift = get_shift(datetime.datetime.time(datetime.datetime.now(ist_tz)))
            self.repository.add(downtime)
        else:
            self.repository.update_downtime(prev_downtimes, reason_id)

    def end_downtime(self, shop_id, equipment_id):
        end_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        self.repository.end_downtime(shop_id, equipment_id, end_time)

    def model_to_dict(self, sorted_model):
        model: MSILDowntime = sorted_model[0]
        machine_name = sorted_model[1]
        model_name = sorted_model[2]
        part_name = sorted_model[3]
        reason = sorted_model[4]
        remark = sorted_model[5]
        downtime_seconds = sorted_model[6] * 60
        downtime_minutes = downtime_seconds // 60
        remaining_seconds = (downtime_seconds % 60) / 100.0
        downtime_duration = downtime_minutes + round(remaining_seconds, 2)
        formatted_downtime_duration = "{:.2f}".format(downtime_duration)
        downtime_duration = formatted_downtime_duration
        if remark == "Other":
            message = model.comment
        else:
            message = remark
        return {
            "id": model.id,
            "machine": machine_name,
            "model": model_name,
            "part_name": part_name,
            "start_time": model.start_time,
            "end_time": model.end_time,
            "duration": downtime_duration,
            "reason": reason,
            "remarks": message,
            "updated_by": model.updated_by
        }

    def get_downtime_report(self, csvwriter, shop_id, machine_list=None,
                            model_list=None, part_name_list=None,
                            start_time=None, end_time=None, start=None, end=None, shift=None,
                            reason=None, remarks=None):

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

        if remarks == [] or remarks == "ALL":
            remarks = None

        if reason == [] or reason == "ALL":
            reason = None

        downtimes = self.repository.get_remarks(shop_id, machine_list=machine_list,
                                                model_list=model_list, part_name_list=part_name_list, start=start,
                                                end=end,
                                                reason=reason, remarks=remarks, start_time=start_time,
                                                end_time=end_time,
                                                shift=shift, limit=1000)

        fields = ['Machine', 'Model', 'Part Name', 'Start Time', 'End Time', 'Duration (Min)', 'Reason', 'Remarks',
                  'Updated By']
        downtime_dict = []
        rows = []
        # csvwriter.writerow(fields)

        for dt in downtimes:
            downtime_dict.append(self.model_to_dict(dt))

        for dt_item in downtime_dict:
            if dt_item['start_time']:
                dt_item['start_time'] = dt_item['start_time'].strftime("%d-%m-%y | %I:%M:%S %p")
            if dt_item['end_time']:
                dt_item['end_time'] = dt_item['end_time'].strftime("%d-%m-%y | %I:%M:%S %p")
            # fields = list(dt_item.values())
            # csvwriter.writerow(fields[1:])
            # rows.append(fields[1:])
        # return rows

        return downtime_dict

    def get_downtime_part_filters(self, shop_id):

        filters = self.repository.get_unique_downtime_filters(shop_id)
        return self.transform_filters(filters)

    def transform_filters(self, filters):
        filter_list = []
        for filter in filters:
            filter_list.append({
                "machine_group": filter[0],
                "machine": filter[1],
                "model": filter[2],
                "part_name": filter[3],
                "reason": filter[4],
                "remark": filter[5]
            })
        return filter_list

    def update_remark_by_downtime_id(self, id, remark, comment, user, shop):
        print("------id-------", id, "---remark---", remark, "---comment----" , comment, "----shop----",shop)
        result = self.repository.new_remark_status(id, remark, comment, user, shop)
        return result

    def downtime_check(self, shop):

        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_minute = datetime.datetime.now(ist_tz).replace(second=0, microsecond=0, tzinfo=None)

        shift = self.shift_repository.get_shift(shop_id=shop, time=cur_minute.time())
        cur_date = self.shift_repository.get_production_date(shift=shift)
        # end_times = self.shift_repository.shift_end_times(shop_id=shop)

        result = self.repository.check_downtime(shop=shop, cur_date=cur_date, shift_param=shift) #, end_times=end_times)
        return result

    # def update_downtime_remark(self,machine,model,part_name,start_time,
    #                            end_time,duration,reason,remarks,comment,shop):

    #     result = self.repository.new_remark_status(
    #             machine,model,part_name,start_time,end_time,duration,reason,remarks,comment,shop)

    #     return result

    # def get_reason_remark_list(self):

    #     remarks_with_reasons = self.repository.get_remark_list()
    #     return remarks_with_reasons

    def get_top5_breakdown_reasons(self,shop_id,start_time,machine_name="ALL"):
        if machine_name == [] or machine_name == "ALL":
            machine_name = None
        result = self.repository.get_top5_breakdown_reasons(shop_id,start_time,machine_name)
        response = []
        for each in result:
            print(each)
            response.append({each[0]: round(each[1], 2)})
        return response
    

    def get_shift_for_new_batch_current_hour(self, current_time):

        """Calculate the next shift based on the current hour for New batch creation.
        Expected value for hour will be 6, 15, 0"""

        if current_time.hour == 6:  # 6:30 AM IST
            return 'A'
        elif current_time.hour == 15: # 3:15 PM IST
            return 'B'
        else:
            return 'C'

    
    def downtime_batch_closure_job(self):
       
        
        current_time = datetime.datetime.now(ist_tz).replace(tzinfo=None) - datetime.timedelta(minutes=10) # Set the end time to current timestamp
        shift,shift_start,shift_end = self.get_shift(current_time)
        date = datetime.datetime.now(ist_tz).date()
        shift_start = datetime.datetime.combine(date=date,time=shift_start)
        shift_end = datetime.datetime.combine(date=date,time=shift_end)
        # logger.info("shift_start = " + str(shift_start) + ", shift_end = " + str(shift_end))
        unfinished_downtimes  = self.repository.get_all_downtimes_with_null_end_time(shift_start=shift_start,shift_end=shift_end)

        if not unfinished_downtimes:
            # logger.info("No unfinished batches found.")
            return

        current_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)  # Set the end time to current timestamp
        shift_time = current_time + datetime.timedelta(hours=1)
        current_shift,shift_start,shift_end  =  self.get_shift(shift_time)

        new_downtimes = []

        for downtime in unfinished_downtimes:
            new_downtimes.append(
                MSILDowntime(
                    equipment_id = downtime.equipment_id,
                    model_id = downtime.model_id,
                    material_code = downtime.material_code,
                    part_2_material_code = downtime.part_2_material_code,
                    start_time = current_time,
                    end_time = None,
                    duration = None,
                    reason_id = downtime.reason_id,
                    remark_id = downtime.remark_id,
                    comment = downtime.comment,
                    shift = current_shift,
                    shop_id = downtime.shop_id,
                    updated_by = downtime.updated_by
                )
            )


            self.repository.update_unfinished_downtimes(downtime.id,current_time)

        self.repository.bulk_insert_downtimes(downtimes_arr=new_downtimes)

