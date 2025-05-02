from ..repositories.msil_report_production_repository import MSILReportProductionRepository
import datetime
from modules.PSM.repositories.models.msil_downtime_reason import MSILDowntimeReasons
from modules.PSM.repositories.msil_report_downtime_repository import MSILReportDowntimeRepository
from modules.PSM.repositories.models.msil_part import MSILPart
from ..repositories.msil_downtime_repository import MSILDowntimeRepository
from..repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from ..repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from ..repositories.msil_equipment_repository import MSILEquipmentRepository
from ..repositories.msil_part_repository import MSILPartRepository
from ..repositories.msil_model_repository import MSILModelRepository
from ..repositories.msil_shift_repository import MSILShiftRepository
from ..repositories.models.msil_downtime import MSILDowntime
import pytz
from .shift_util import get_shift, get_production_date
ist_tz = pytz.timezone('Asia/Kolkata')


class MSILReportDowntimeService:
    def __init__(self, repository: MSILReportDowntimeRepository, shift_repo: MSILShiftRepository):
        self.repository = repository
        self.shift_repository = shift_repo

    def get_downtime_data(self, shop_id, start_date, end_date, machine_list=None,
                          model_list=None, part_name_list=None, shift=None):
        try:
            first_shift_time = self.shift_repository.day_start_time(shop_id=shop_id)
            shifts_list = self.shift_repository.shift_object_list(shop_id=shop_id)
            result = self.repository.get_downtime_data(shop_id, start_date, end_date,shifts_list,first_shift_time,machine_list, model_list, part_name_list, shift)
            return result
        
        except Exception as e:
            print(f"Error in get_machine_downtime_data: {str(e)}")
            return e

        
    def get_reports_downtime_report(self, csvwriter, shop_id,start_date, end_date,machine_list=None,
                            model_list=None, part_name_list=None, shift = None):
        if machine_list == [] or machine_list == "ALL":
            machine_list = None
        
        if model_list == [] or model_list == "ALL":
            model_list = None
        
        if part_name_list == [] or part_name_list == "ALL":
            part_name_list = None

        if shift == [] or shift == "ALL":
            shift = None

        first_shift_time = self.shift_repository.day_start_time(shop_id=shop_id)
        shifts_list = self.shift_repository.shift_object_list(shop_id=shop_id)

        report_downtime = self.repository.get_downtime_data(shop_id=shop_id, start_date=start_date, end_date = end_date,
                                                            machine_list=machine_list ,model_list=model_list,shifts_list=shifts_list,
                                                            part_name_list=part_name_list, shift=shift,first_shift_time=first_shift_time )

        fields = ['Machine', 'Shift', 'Total Working Time','Running Time',
                  'Idle Downtime','Breakdown Downtime','Scheduled Downtime','Idle Reason', 'Idle Reason Count', 'Breakdown Reason' , 'Breakdown Reason Count', 'Scheduled Reason', 'Scheduled Reason Count']
        downtime_dict = []
        rows = []
        csvwriter.writerow(fields)

        for dt in report_downtime:
            machine_name = dt['machine_name']
            for shift_name, shift_details in dt.items():
                if shift_name != 'machine_name':
                    for shift_data in shift_details:
                        row = {
                            "machine": machine_name,
                            "Shift": shift_data['name'],
                            "Total Working Time": shift_data['total_working_time'],
                            "Running Time": shift_data['running_time'],
                            "Idle Downtime": shift_data['idle_downtime'],
                            "Breakdown Downtime": shift_data['breakdown_downtime'],
                            "Scheduled Downtime": shift_data['scheduled_downtime']
                        }
                        idle_reasons = shift_data['idle_reasons']
                        for reason_data in idle_reasons:
                            row["Idle Reason"] = reason_data['reason']
                            row["Idle Reason Count"] = reason_data['count']
                            downtime_dict.append(row.copy())
                        if not idle_reasons:
                            row["Idle Reason"] = ''
                            row["Idle Reason Count"] = ''


                        breakdown_reasons = shift_data['breakdown_reasons']
                        for reason_data in breakdown_reasons:
                            row["Breakdown Reason"] = reason_data['reason']
                            row["Breakdown Reason Count"] = reason_data['count']
                            downtime_dict.append(row.copy())
                        if not breakdown_reasons:
                            row["Breakdown Reason"] = ''
                            row["Breakdown Reason Count"] = ''
                        
                        scheduled_reasons = shift_data['scheduled_reasons']
                        for reason_data in scheduled_reasons:
                            row["Scheduled Reason"] = reason_data['reason']
                            row["Scheduled Reason Count"] = reason_data['count']
                            downtime_dict.append(row.copy())
                        if not scheduled_reasons:
                            row["Scheduled Reason"] = ''
                            row["Scheduled Reason Count"] = ''
           
        return downtime_dict
        # for dt_item in downtime_dict:
        #     fields = list(dt_item.values())
        #     csvwriter.writerow(fields)
        #     rows.append(fields)
        # return rows