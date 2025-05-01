from ..repositories.msil_report_production_repository import MSILReportProductionRepository
import datetime
from modules.PSM.repositories.models.msil_quality_punch_record import MSILQualityPunchingRecord
from modules.PSM.repositories.models.msil_quality_reason import MSILQualityReasons
from modules.PSM.repositories.models.msil_quality_remark import MSILQualityRemarks

from modules.PSM.repositories.models.msil_quality_updation import MSILQualityUpdation
from ..repositories.msil_equipment_repository import MSILEquipmentRepository
from ..repositories.msil_part_repository import MSILPartRepository
from ..repositories.msil_model_repository import MSILModelRepository
from ..repositories.models.msil_quality_punching import MSILQualityPunching
from ..repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
from ..repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
from ..repositories.msil_report_quality_repository import MSILReportQualityRepository


import pytz

class MSILReportQualityService:
    def __init__(self, repository: MSILReportQualityRepository):
                #  , eqp_repo:MSILEquipmentRepository, part_repo:MSILPartRepository, model_repo:MSILModelRepository, updation_repo:MSILQualityUpdationRepository):
        self.repository = repository
        # self.equipment_repository = eqp_repo
        # self.part_repository = part_repo
        # self.model_repository = model_repo 
        # self.update_repository = updation_repo 

    def get_report_filters(self, shop_id):
        
        filters = self.repository.get_unique_report_filters(shop_id)
        return self.transform_filters(filters)
    
    def transform_filters(self,filters):
        filter_list = []
        for filter in filters:
            filter_list.append({
                "machine_group" : filter[0],
                "machine" : filter[1],
                "model" : filter[2],
                "part_name" : filter[3]
            })
        return filter_list
    
    def get_machine_quality_data(self, shop_id, start_date, end_date, machine_list=None, model_list=None, part_name_list=None, shift=None):
        try:
            quality_data = self.repository.get_machine_quality_data(shop_id, start_date, end_date, machine_list, model_list, part_name_list, shift)
            return quality_data

        except Exception as e:
            print(f"Error in get_machine_quality_data: {str(e)}")
            return e
        
    def get_reports_quality_report(self, csvwriter, shop_id,start_date, end_date,machine_list=None,
                            model_list=None, part_name_list=None, shift = None):
        if machine_list == [] or machine_list == "ALL":
            machine_list = None
        
        if model_list == [] or model_list == "ALL":
            model_list = None
        
        if part_name_list == [] or part_name_list == "ALL":
            part_name_list = None

        if shift == [] or shift == "ALL":
            shift = None

        report_quality = self.repository.get_machine_quality_data( shop_id, start_date, end_date,
                                                            machine_list ,model_list,
                                                            part_name_list , shift )

        fields = ['Machine',  'Shift Name','Hold Qty', 'Reject Qty', 
                'Pending Rework Qty', 'Recylcle Qty', 'Ok Qty','Reason', 'Count', 'Quantity']
        quality_dict = []
        rows = []
        csvwriter.writerow(fields)

        for qt in report_quality:
            machine_name = qt['machine_name']
            for shift_name, shift_data in qt.items():
                if shift_name != 'machine_name':
                    row = {
                    "machine": machine_name,
                    "Shift Name": shift_name,
                    "Hold Qty": shift_data['hold_qty'],
                    "Reject Qty": shift_data['reject_qty'],
                    # "Rework Qty": shift_data['rework_qty'],
                    "Pending Rework Qty":shift_data['pending_rework_qty'],
                    "Recycle Qty": shift_data['recycle_qty'],
                    "Ok Qty": shift_data['ok_qty']
                    }
                    quality_reasons = shift_data['reasons']
                    if quality_reasons == []:
                        quality_dict.append(row.copy())
                    else:
                        for reason_data in quality_reasons:
                            row["Reason"] = reason_data['reason']
                            row["Count"] = reason_data['count']
                            row["Quantity"] = reason_data['quantity']
                            quality_dict.append(row.copy())

        return quality_dict
        # for qt_item in quality_dict:
        #     fields = list(qt_item.values())
        #     csvwriter.writerow(fields)
        #     rows.append(fields)
        # return rows