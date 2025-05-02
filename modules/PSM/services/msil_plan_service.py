from ..repositories.msil_plan_repository import MSILPlanRepository
from ..repositories.msil_equipment_repository import MSILEquipmentRepository
from ..repositories.msil_part_repository import MSILPartRepository
from ..repositories.msil_variant_repository import MSILVariantRepository
from ..repositories.models.msil_plan import MSILPlan, PlanStatusEnum
from ..repositories.models.msil_alert_notification import AlertNotification
from ..repositories.msil_alert_repository import MSILAlertRepository
from ..repositories.msil_model_repository import MSILModelRepository
from ..services.msil_alert_service import MSILAlertService
from modules.PSM.repositories.models.msil_plan import MSILPlan, PlanStatusEnum
from modules.PSM.repositories.models.msil_part import MSILPart
from modules.PSM.repositories.models.msil_model import MSILModel
from modules.PSM.repositories.models.msil_batch import MSILBatch
from modules.PSM.repositories.models.msil_shift import MSILShift
from modules.PSM.repositories.models.msil_production import MSILProduction
from modules.PSM.repositories.models.msil_equipment import MSILEquipment
from modules.PSM.repositories.models.shop_configuration import ShopConfiguration
from modules.PSM.repositories.models.msil_alert_notification import AlertNotification
from sqlalchemy import (
    and_,
    desc,
    func,
    case,
    not_    
)
from ..repositories.msil_plan_file_status_repository import MSILPlanFileStatusRepository
from ..repositories.models.msil_plan_file_status import MSILPlanFileStatus, PlanFileStatusEnum
from .service import Service
import datetime
import pytz
import time
from pandas import (
    read_excel,
    isnull,
    isna,
    to_datetime,
    notna,
    Timestamp,
    ExcelWriter
)
import pandas as pd
# from openpyxl import load_workbook
# import xlsxwriter
import numpy

ist_tz = pytz.timezone('Asia/Kolkata')


class PlanSheetValidationError(Exception):
    def __init__(self):
        self.error_list = []

    def add_error(self, error):
        self.error_list.append(error)

    def get_error_list(self):
        return self.error_list


class MSILPlanService(Service):
    def __init__(self, repository: MSILPlanRepository, part_repo: MSILPartRepository, eqp_repo: MSILEquipmentRepository,
                 var_repo: MSILVariantRepository, mod_repo: MSILModelRepository, alert_repo: MSILAlertRepository,
                 status_repo: MSILPlanFileStatusRepository):
        self.repository = repository
        self.ps_part_repository = part_repo
        self.ps_equipment_repository = eqp_repo
        self.msil_variant_repository = var_repo
        self.msil_alert_repository = alert_repo
        self.msil_model_repository = mod_repo
        self.msil_status_repository = status_repo
        self.machine_names = {}
        self.model_names = {}
        self.part_names = {}
        self.pe_codes = {}
        self.variant_names = {}
        self.part_numbers = {}

        super().__init__(repository, self.transform_model_to_dict, self.transform_dict_to_model)

    def is_all_null(self, row_data):
        return all(isna(each) for each in row_data)

    def get_work_orders(self, parts, production_date, shop_id):
        work_orders = self.repository.get_work_orders(shop_id, parts, production_date)
        orders = {}
        for work_order in work_orders:
            orders[work_order.output_part] = work_order.work_order_number
        return orders

    def get_plans(self, shop_id, machine_list=None,
                  model_list=None, part_name_list=None,
                  pe_code_list=None, production_date_list=None,
                  shift=None,
                  priority=None,
                  status=None,
                  sort_priority=None,
                  page_no=1, page_size=10):


        if machine_list == [] or machine_list == "ALL":
            machine_list = None

        if model_list == [] or model_list == "ALL":
            model_list = None

        if part_name_list == [] or part_name_list == "ALL":
            part_name_list = None

        if pe_code_list == [] or pe_code_list == "ALL":
            pe_code_list = None

        if production_date_list == [] or production_date_list == "ALL" or production_date_list is None:
            production_date_list = [datetime.datetime.now().date()]

        if shift == "ALL":
            shift = None

        if priority == "ALL":
            priority = None

        if status == "ALL":
            status = None

        plans = self.repository.get_sorted_plans(shop_id,
                                                 machine_list=machine_list,
                                                 model_list=model_list, part_name_list=part_name_list,
                                                 pe_code_list=pe_code_list, production_date_list=production_date_list,
                                                 shift=shift,
                                                 priority=priority,
                                                 sort_priority=sort_priority,
                                                 status=status, limit=page_size, offset=(page_no - 1) * page_size)
        return self._Service__transform_model_list(plans)

    def get_plans_report(self, csvwriter, shop_id, machine_list=None,
                         model_list=None, part_name_list=None,
                         pe_code_list=None, production_date_list=None,
                         shift=None,
                         priority=None,
                         status=None,
                         sort_priority=None):
        if machine_list == [] or machine_list == "ALL":
            machine_list = None

        if model_list == [] or model_list == "ALL":
            model_list = None

        if part_name_list == [] or part_name_list == "ALL":
            part_name_list = None

        if pe_code_list == [] or pe_code_list == "ALL":
            pe_code_list = None

        if production_date_list == [] or production_date_list == "ALL":
            production_date_list = None

        if shift == "ALL":
            shift = None

        if priority == "ALL":
            priority = None

        if status == "ALL":
            status = None

        plans = self.repository.get_sorted_plans(shop_id,
                                                 machine_list=machine_list,
                                                 model_list=model_list, part_name_list=part_name_list,
                                                 pe_code_list=pe_code_list, production_date_list=production_date_list,
                                                 shift=shift,
                                                 priority=priority,
                                                 sort_priority=sort_priority,
                                                 status=status, limit=10000, offset=0)
        fields = ["Machine", "Model", "Part name", "P E Code", "Production number", "Production date", "Shift",
                  "Priority", "Planned Qty", "Actual Qty", "Status"]
        
        result = []
        for each in plans:
            model: MSILPlan = each[0]
            model_name = each[1]
            part_name = each[2] + f"({each[5]})" if each[5] else each[2]
            result.append({
                "Machine": each[4],
                "Model": model_name,
                "Part Name": part_name,
                "PE Code": each[3],
                "Production number": model.work_order_number,
                "Production Date": model.production_date,
                "Shift": model.shift,
                "Priority": model.priority,
                "Planned Quantity": model.planned_quantity,
                "Actual Quantity": each[7] or 0,
                "Status": model.status.name
            })

        return result

        # csvwriter.writerow(fields)
        # rows = []
        # for each in plans:
        #     model: MSILPlan = each[0]
        #     model_name = each[1]
        #     if each[5]:
        #         part_name = each[2] + "(" + each[5] + ")"
        #     else:
        #         part_name = each[2]
        #     fields = [
        #         each[4],
        #         model_name,
        #         part_name,
        #         each[3],
        #         model.work_order_number,
        #         model.production_date,
        #         model.shift,
        #         model.priority,
        #         model.planned_quantity,
        #         each[7] or 0,
        #         model.status.name
        #     ]
        #     csvwriter.writerow(fields)
        #     rows.append(fields)
        # return rows

    def validate_future_dates(self, df_plan, errors):
        today = datetime.datetime.now(ist_tz).date()
        future_dates = []
        for date_column in df_plan.columns:
            if isinstance(date_column, datetime.datetime) and date_column.date() >= today:
                future_dates.append(date_column.date())

        if len(future_dates) > 30:

            errors.append("The Plan Excel should have a maximum of 30 days data in future dates.")

        return errors

    def validate_previous_shift_data(self, shop_id, df_plan, pe):
        cur_minute = datetime.datetime.now(ist_tz).replace(second=0, microsecond=0, tzinfo=None)
        current_shift = self.repository.get_shift(shop_id=shop_id, time=cur_minute.time())
        today = datetime.datetime.now(ist_tz).date()

        for date_column in df_plan.columns:
            if isinstance(date_column, datetime.datetime) and date_column.date() == today:
                if 'Shift' in df_plan.columns and not df_plan['Shift'].isnull().all():
                    previous_shift_data = df_plan[
                        (df_plan['Shift'] < current_shift)
                    ]
                    if not previous_shift_data.empty:
                        pe.append("Cannot upload previous shift data for the current day.")
                        # errors.append("Cannot upload previous shift data for the current day.")
                # Perform further operations using `previous_shift_data`
                else:
                    # Handle case where 'Shift' column is all null
                    # For example, print a message or perform alternative actions
                    pe.append("Shift column should not be null for any row when the "
                                  "shop is configured at shift level")
                    # errors.append("Shift column should not be null for any row when the "
                    #               "shop is configured at shift level")

        return pe

    def validate_previous_day_data(self, shop_id, df_plan, warnings):
        today = datetime.datetime.now(ist_tz).date()
        previous_dates = []
        for date_column in df_plan.columns:
            if isinstance(date_column, datetime.datetime) and date_column.date() < today:
                previous_dates.append(date_column.date())

        for date in previous_dates:
            warnings.append(f"Previous data of date {date} is being present in sheet. Please try again after deleting it")

        return warnings

    def get_machine_details(self, shop_id, machines):
        machine_details = self.ps_equipment_repository.check_for_machines(shop_id=shop_id,
                                                                          machine_names=machines)
        return machine_details

    def get_variant_details(self, variants):
        variant_details = self.msil_variant_repository.check_for_variants(variant_names=variants)
        return variant_details

    def get_name_details(self, part_names):
        name_details = self.ps_part_repository.check_for_names(part_names=part_names)
        return name_details

    def get_number_details(self, part_numbers):
        number_details = self.ps_part_repository.check_for_numbers(part_numbers=part_numbers)
        return number_details

    def get_code_details(self, pe_codes):
        
        code_details = self.ps_part_repository.check_for_codes(part_codes=pe_codes)
        return code_details

    def get_model_details(self,shop_id, model_names):
        model_details = self.msil_model_repository.check_for_models(shop_id=shop_id, model_names=model_names)
        return model_details

    def validate_plan_data(self, df_plan, shop_id, error_remarks, is_shift, is_day):
        eqp_id = {}
        var_id = {}
        mod_id = {}
        part_list = []

        today =  datetime.datetime.now(ist_tz).date()
        # pe = PlanSheetValidationError()
        df_plan = df_plan.replace('^\s+$', numpy.nan, regex=True)
        unique_cols = ['Machine', 'Model', 'PE Code', 'Part Number', 'Part Name', 'Variant', 'Shift']
        if any(
                df_plan.duplicated(
                    unique_cols
                )
        ):
            error_remarks.append(
                f"There are multiple entries in Plan Sheet"
                f" at indices"
                f"{list(map(lambda x: x + 2, list(df_plan[df_plan.duplicated(unique_cols)].index)))}")

        # p_headers = {'Machine', 'Model', 'PE Code', 'Part Number', 'Part Name', 'Variant', 'Shift'}
        # p_missing = p_headers - set(df_plan.head())
        # p_extra = set(df_plan.head()) - p_headers

        # if p_missing:
        #     pe.add_error(f"Column(s) {p_missing} Missing in Working plan sheet.")
        #     raise pe
        
        # if any(
        #         df_plan.duplicated(
        #             unique_cols
        #         )
        # ):
        #     error_remarks.append(
        #         f"There are multiple entries in Plan Sheet"
        #         f" at indices"
        #         f"{list(map(lambda x: x + 2, list(df_plan[df_plan.duplicated(unique_cols)].index)))}")

        # Handling duplicates
        # p_duplicates = df_plan[df_plan.duplicated(keep=False)]
        # if not p_duplicates.empty:
        #     self.plan_alert(f"Duplicate entries for rows {', '.join(map(str, p_duplicates.index))} in Plan Data",
        #                     shop_id)
        # df_plan.drop_duplicates(keep='first', inplace=True)

        today_column_exists = False
        today_column_name = None
        for date_column in df_plan.columns:
            # Check if column is a date and matches today's date
            if isinstance(date_column, datetime.datetime) and date_column.date() == today:
                today_column_exists = True
                today_column_name = date_column
                break
        
        if today_column_exists:
            if df_plan[today_column_name].isnull().all():
                error_remarks.append(f"Planned quantity for today ({today}) is missing in all rows.")
        else:
            error_remarks.append(f"Planned quantity column for today ({today}) is missing.")
        

        # error_remarks = self.validate_future_dates(df_plan, error_remarks)
        # if pe:
        #     pe.add_error(error_remarks)
        #     raise pe
        # df_plan['Shift'] = df_plan['Shift'].fillna('_')
        # df_plan['Planned Qty'] = 0
        # df_plan['Sequence'] = 0
        # df_plan['Production Date']=datetime.datetime.now(ist_tz).date()
        for date_column in df_plan.columns:
            if date_column not in unique_cols and isinstance(date_column, datetime.datetime) == False:
                error_remarks.append(f"{date_column} Column is not allowed in Plan sheet")

        
        # iterating over df_plan to check for null items
        for index_label, row in df_plan.iterrows():
            if self.is_all_null(row):
                continue
            
            for date_column in df_plan.columns:
                # Exclude non-date columns and check if column is a valid datetime object and date is >= today
                if date_column not in ['Model', 'Variant', 'Part Name', 'Line', 'Shift'] and isinstance(date_column, datetime.datetime) and date_column.date() >= today:
                    value = row.get(date_column)  # Store the value to avoid redundant calls

                    if pd.isna(value) or value is None:
                        continue  # Skip if the value is NaN or None

                    # Check if the value is numeric (int or float)
                    if not isinstance(value, (int, float)):
                        error_remarks.append(f"Value at {date_column.date()},{index_label + 1} is not int")
                    elif value < 0:  # Ensure the numeric value is non-negative
                        error_remarks.append(f"Value at {date_column.date()},{index_label + 1} cannot be negative")


                if date_column == None or date_column == 'NaN':
                    error_remarks.append("Missing Date Column ")

            part_list.append({
                "row_number": str(index_label + 2),
                "model_name": row['Model'],
                "machine_name": str(row['Machine']),
                "part_number": row['Part Number'],
                "part_name": row['Part Name'],
                "pe_code": row['PE Code']
            })



            if isna(str(row['Machine'])):
                error_remarks.append(f"Machine: Missing Row {index_label + 2} in Working plan")
            elif not isinstance(row['Machine'], str):
                error_remarks.append(f"Machine: invalid machine is present at Row {index_label+2} in Working plan")
            else:
                if self.machine_names.get(str(row['Machine']), None) == None:
                    self.machine_names[str(row['Machine'])] = [index_label + 2]
                else:
                    self.machine_names[str(row['Machine'])].append(index_label + 2)

            if isna(row['Model']):
                error_remarks.append(f"Model: Missing Row {index_label + 2} in Working plan")
            elif not isinstance(row['Model'], str):
                error_remarks.append(f"Model: invalid model is present at Row {index_label+2} in Working plan")
            else:
                if self.model_names.get(row['Model'], None) == None:
                    self.model_names[row['Model']] = [index_label + 2]
                else:
                    self.model_names[row['Model']].append(index_label + 2)

            if isna(row['PE Code']):
                error_remarks.append(f"PE Code: Missing Row {index_label + 2} in Working plan")
            elif not isinstance(row['PE Code'], str):
                error_remarks.append(f"PE Code: invalid pe code is present at Row {index_label+2} in Working plan")
            else:
                if self.pe_codes.get(row['PE Code'], None) == None:
                    self.pe_codes[row['PE Code']] = [index_label + 2]
                else:
                    self.pe_codes[row['PE Code']].append(index_label + 2)

            if notna(row['Variant']):
                if not isinstance(row['Variant'], str):
                    error_remarks.append(f"Variant: invalid variant is present at Row {index_label+2} in Working plan")
                elif self.variant_names.get(row['Variant'], None) == None:
                    self.variant_names[row['Variant']] = [index_label + 2]
                else:
                    self.variant_names[row['Variant']].append(index_label + 2)

            if isna(row['Part Name']):
                error_remarks.append(f"Part Name: Missing Row {index_label + 2} in Working plan")
            elif not isinstance(row['Part Name'], str):
                    error_remarks.append(f"Part Name: invalid part name is present at Row {index_label+2} in Working plan")
            else:
                if self.part_names.get(row['Part Name'], None) == None:
                    self.part_names[row['Part Name']] = [index_label + 2]
                else:
                    self.part_names[row['Part Name']].append(index_label + 2)

            if isna(row['Part Number']):
                error_remarks.append(f"Part Number: Missing Row {index_label + 2} in Working plan")
            elif not isinstance(row['Part Number'], str) :
                error_remarks.append(f"Part Number: Invalid Part Number {index_label+2} is present in Working plan")
            else:
                if self.part_numbers.get(row['Part Number'], None) == None:
                    self.part_numbers[row['Part Number']] = [index_label + 2]
                else:
                    self.part_numbers[row['Part Number']].append(index_label + 2)
            if is_day:
                if isna(row["Shift"]):
                    pass
                else:
                    error_remarks.append(f"shop is configured in day wise shift data cannot be entered")
            if is_shift:
                if row['Shift'] not in ['_', 'A', 'B', 'C']:
                    error_remarks.append(f"Shift is invalid for Row {index_label + 2} in Working plan")

            if is_shift and isna(row["Shift"]):
                error_remarks.append(f"Shift : missing row {index_label + 2} in working Plan")

            # if is_day and row["Shift"] != None:
            #     error_remarks.append(
            #         f"Shift error : shop is configured as day wise cannot contain the shift and {index_label + 2}")

        # validating from master data
        if not error_remarks:
            machines = list(set(self.machine_names.keys()))
            machine_details = self.get_machine_details(shop_id, machines)
            mac_list = list(set(machine_details.keys()))
            if len(machine_details) != len(self.machine_names):
                for item in machines:
                    if item not in mac_list:
                        for i in self.machine_names[item]:
                            error_remarks.append(f"Machine not present in system for Row {i}")

            names = list(set(self.part_names.keys()))
            name_details = self.get_name_details(names)
            name_list = list(item[0] for item in name_details)
            if len(name_details) != len(self.part_names):
                for item in names:
                    if item not in name_list:
                        for i in self.part_names[item]:
                            error_remarks.append(f"Part Name not present in system for Row {i}")

            numbers = list(set(self.part_numbers.keys()))
            number_details = self.get_number_details(numbers)
            number_list = list(item[0] for item in number_details)
            if len(number_details) != len(self.part_numbers):
                for item in numbers:
                    if item not in number_list:
                        for i in self.part_numbers[item]:
                            error_remarks.append(f"Part Number not present in system for Row {i}")

            codes = list(set(self.pe_codes.keys()))
            code_details = self.get_code_details(codes)
            code_list = list(item[0] for item in code_details)
            if len(code_details) != len(self.pe_codes):
                for item in codes:
                    if item not in code_list:
                        for i in self.pe_codes[item]:
                            error_remarks.append(f"PE Code not present in system for Row {i}")

            models = list(set(self.model_names.keys()))
            model_details = self.get_model_details(shop_id, models)
            model_list = list(set(model_details.keys()))
            if len(model_details) != len(self.model_names):
                for item in models:
                    if item not in model_list:
                        for i in self.model_names[item]:
                            error_remarks.append(f"Model not present in system for Row {i}")

            variants = list(set(self.variant_names.keys()))
            variant_details = self.get_variant_details(variants)
            variant_list = list(set(variant_details.keys()))
            if len(variant_details) != len(self.variant_names):
                for item in variants:
                    if item not in variant_list:
                        for i in self.variant_names[item]:
                            error_remarks.append(f"Variant not present in system for Row {i}")

            invalid_combinatons = self.ps_part_repository.check_parts(part_list)
            for invalid_row in invalid_combinatons:
                error_remarks.append(
                    f"Machine, Model, PE Code, Part Number, Part Name combination is not present in the system for Row {invalid_row}")

        return error_remarks

    def get_plan_cache(self,shop_id):
        today = datetime.datetime.now(ist_tz).date()
        data = self.repository.get_plan_cache(today,shop_id=shop_id)
        return self.transform_plan(data)
    
    def transform_plan(self,data):
        plan_arr = []
        plan_dict = {}
        for each in data:
            plan_obj = self.get_plan_obj(each.equipment_id,each.variant_id,each.model_id,each.material_code,each.shift,plan_arr)
            plan_obj['metrics'][each.production_date] = each.id

        for plan_obj in plan_arr:
            if plan_obj.get('shift') not in ['A','B','C']:
                plan_obj['shift']=None
            plan_dict[str(plan_obj.get('equipment_id'))+ '_'+
                      str(plan_obj.get('variant_id'))+'_'+
                      str(plan_obj.get('model_id'))+'_'+
                      str(plan_obj.get('material_code'))+"_"+
                      str(plan_obj.get('shift'))] = plan_obj.get('metrics')
        return plan_dict

    def get_plan_obj(self,equipment_id,variant_id,model_id,material_code,shift,plan_arr=[]):
        if (len(plan_arr) > 0 and
            plan_arr[-1].get('equipment_id') == equipment_id and
            plan_arr[-1].get('variant_id') == variant_id and
            plan_arr[-1].get('model_id') == model_id and
            plan_arr[-1].get('material_code') == material_code and
            plan_arr[-1].get('shift') == shift):
            plan_obj = plan_arr[-1]
        else:
            plan_obj = {
                'equipment_id' : equipment_id,
                'variant_id' : variant_id,
                'model_id' : model_id,
                'material_code' : material_code,
                'shift' : shift,
                'metrics'  : {}
            }
            plan_arr.append(plan_obj)
        return plan_obj


    def process_plan_data(self, df_plan, shop_id,  error_remarks, is_shift):
        plan_cache = self.get_plan_cache(shop_id=shop_id) 
        today =  datetime.datetime.now(ist_tz).date()
        plans_created = []
        updates = []
        machine_details = self.get_machine_details(shop_id, list(set(self.machine_names.keys())))
        part_details = self.get_name_details(list(set(self.part_names.keys())))
        part_number_details = self.get_number_details(list(set(self.part_numbers.keys())))
        code_details = self.get_code_details(list(set(self.pe_codes.keys())))
        model_details = self.get_model_details(shop_id, list(set(self.model_names.keys())))
        variant_details = self.get_variant_details(list(set(self.variant_names.keys())))



        df_plan['Shift'] = df_plan['Shift'].fillna('_')
        df_plan['Planned Qty'] = 0
        df_plan['Planned Qty Hourly'] = 0
        # df_plan['Stock Out Time'] = 0
        df_plan['Sequence'] = 0
        df_plan['Production Date'] = datetime.datetime.now(ist_tz).date()
        #
        # df_plan['Planned Qty'] = planned_quantities_list
        # df_plan['Planned Qty Hourly'] = (df_plan['Planned Qty'] / 16).fillna(0)
        # df_plan['Stock Out Time'] = (
        #             (df_plan['Stock PRS-M'] + df_plan['Stock Vendor']) / df_plan['Planned Qty Hourly']).replace(
        #     numpy.inf, 0)
        # df_plan['Stock Out Time'] = df_plan['Stock Out Time'].apply(lambda x: 0 if x < 0 else (30 if x > 30 else x))
        #
        # df_plan.sort_values(by=['Machine', 'Stock Out Time'], inplace=True)
        # mask = df_plan['Planned Qty'].notnull()
        # df_plan['Sequence'] = df_plan[mask].groupby(['Machine']).cumcount() + 1
        # df_plan['Planned Qty'] = df_plan['Planned Qty'].fillna(0)
        # df_plan['Sequence'] = df_plan['Sequence'].fillna(0)
        priority_counter = {}
        for index_label, row in df_plan.iterrows():
            
            planned_quantities = {}
            

            if self.is_all_null(row):
                continue

            for date_column in df_plan.columns:
                if date_column not in ['Machine', 'Model', 'PE Code', 'Part Number', 'Part Name', 'Variant', 'Shift'] and isinstance(date_column,
                                                                                                        datetime.datetime) and date_column.date() >= today:  # Exclude non-date columns:  # Exclude non-date columns
                    if isna(row.get(date_column)) or row.get(date_column) == None or row.get(date_column) == 0:
                        pass

                    else:
                        planned_quantities[date_column.date()] = row.get(date_column)
                        if date_column.date() not in priority_counter.keys():
                            priority_counter[date_column.date()] = 1
                        else:
                            priority_counter[date_column.date()] +=1

            variant_id = variant_details.get(row['Variant'], None)
            model_id = model_details.get(row['Model'], None)
            equipment_id = machine_details[str(row['Machine'])]
            part_number = row['Part Number']
            pe_code = row['PE Code']
            shift = row["Shift"]
            if shift not in ['A','B','C']:
                shift = None
            existing_production_dates = plan_cache.get(str(equipment_id)+"_"+str(variant_id)+'_'+str(model_id)+'_'+str(part_number)+'_'+str(shift),{})

            production_dates_need_to_be_entered = set(planned_quantities.keys()) - set(
                existing_production_dates.keys())
            for date, plan_id in existing_production_dates.items():
                if planned_quantities[date] is not None:
                    updates.append({
                        "id": plan_id,
                        "planned_quantity": planned_quantities[date],
                        "priority": priority_counter[date]
                    })
            for date in production_dates_need_to_be_entered:
                Plan = MSILPlan()
                Plan.equipment_id = machine_details[str(row['Machine'])]
                if notna(row['Variant']):
                    Plan.variant_id = variant_details[row['Variant']]
                else:
                    Plan.variant_id = None
                if notna(row['Shift']) and isinstance(row['Shift'], str):
                    Plan.shift = row['Shift'].upper()
                else:
                    Plan.shift = None
                Plan.lot_size = None
                Plan.model_id = model_details[row['Model']]
                Plan.material_code = row['Part Number']
                Plan.work_order_number = f"{date}_{row['Part Number']}"
                Plan.production_date = date
                Plan.priority = priority_counter[date]
                # Plan.variant_id = variant_details[row["Variant"]]
                Plan.planned_quantity = planned_quantities[date]
                Plan.actual_quantity = 0
                Plan.status = PlanStatusEnum.PLANNED
                Plan.shop_id = shop_id
                plans_created.append(Plan)
        self.repository.bulk_update_existing_plans(updates)
        self.repository.insert_plan(plans_created)
        self.update_plan_status(shop_id, date)
        return plans_created


    def parse_and_add_plans(self, file_obj, shop_id, writer=None, pre_plan=None):
        error_remarks = []
        warnings =[]
        pe = PlanSheetValidationError()
        today = datetime.datetime.now(ist_tz).date()
        # try:
        try:

            df_plan = read_excel(file_obj, sheet_name='Working Plan', engine='openpyxl')

        except Exception as e:
            print(str(e))
            pe.add_error(str(e))
            raise pe
        # Validate file format and read Excel data
        required_columns = ['Machine', 'Model', 'PE Code', 'Part Number', 'Part Name', 'Variant', 'Shift']
        if not all(col in df_plan.columns for col in required_columns):
            error_remarks.append("Missing required columns in the Plan Excel.")
            raise pe
            # error_remarks.append("Missing required columns in the Plan Excel.")

        date_column = []
        for col in df_plan.columns:
            if isinstance(col, datetime.datetime):
                date_column.append(col)
        
        if len(date_column)<1:
            error_remarks.append("Missing date columns in the Plan Excel")
            raise pe

        self.msil_status_repository.new_status(today, PlanFileStatusEnum.INPROGRESS, None, shop_id)

        # Validate future dates
        error_remarks = self.validate_future_dates(df_plan, error_remarks)

        is_day, is_shift = self.repository.get_shop_configuration(shop_id)

        if is_shift:
            print("this is a shift configured shop")
            error_remarks = self.validate_previous_shift_data(shop_id, df_plan, error_remarks)
        if is_day:
            print("this is a day configured shop")
            error_remarks = self.validate_previous_day_data(shop_id, df_plan, error_remarks)

        if len(error_remarks) != 0:
            self.msil_status_repository.new_status(today, PlanFileStatusEnum.FAILED, error_remarks, shop_id)
            return error_remarks

        # Validate and process the plan data
        st = time.time()
        error_remarks = self.validate_plan_data(df_plan, shop_id, error_remarks, is_shift, is_day)
        et = time.time()
        print("time taken in validate_plan_data : ",et-st)
        if len(error_remarks) != 0:
            # self.msil_status_repository.new_status(today, PlanFileStatusEnum.FAILED, error_remarks, shop_id)
            print(error_remarks)
            return error_remarks
        else:
            st = time.time()
            self.mark_unplanned_quantities_in_plan(df_plan=df_plan, shop_id=shop_id)
            et = time.time()
            print("time taken in mark_unplanned_quantities_in_plan : ",et-st)
            st = time.time()
            plan_created = self.process_plan_data(df_plan, shop_id, error_remarks, is_shift)
            et = time.time()
            print("time taken in new_status : ",et-st)                
            self.msil_status_repository.new_status(today, PlanFileStatusEnum.SUCCESS, None, shop_id)
            if writer:
                df_plan.to_excel(writer, sheet_name='Working plan', index=False)
                writer.save()
        return plan_created
        # except PlanSheetValidationError as e:
        #     errors = ('; '.join(pe.get_error_list()))
        #     print(errors)
        #     self.msil_status_repository.new_status(today, PlanFileStatusEnum.FAILED, errors, shop_id)
        #     self.plan_alert(errors, shop_id)
        #     return errors
        # except Exception as e:
        #     self.msil_status_repository.new_status(today, PlanFileStatusEnum.FAILED, str(e), shop_id)
        #     self.plan_alert(str(e), shop_id)
        #     return str(e)


    def mark_unplanned_quantities_in_plan(self, df_plan, shop_id):
        planned_quantities = {}
        today = datetime.datetime.now(ist_tz).date()
        for date_column in df_plan.columns:
            if date_column not in [] and isinstance(date_column, datetime.datetime) and date_column.date() >= today:  # Exclude non-date columns
                planned_quantities[date_column.date()] = 0

        for date in planned_quantities.keys():
            self.repository.marking_all_the_planned_quantities_as_unplanned(shop_id=shop_id, date=date)

    def update_plan_status(self, shop_id=None,
                           production_date=None):
        plan_data = self.repository.get_plan_datewise(shop_id=shop_id, production_date=production_date)
        for each in plan_data:
            id, actual_qty, planned_qty, status = each
            if actual_qty is None:
                actual_qty = 0 
            updates = []
            if int(actual_qty) < int(planned_qty) and status != PlanStatusEnum.PLANNED.value:
                updates.append({
                    'id' : id,
                    'status' : PlanStatusEnum.PLANNED.value
                })
            if int(planned_qty) > 0 and int(actual_qty) >= int(planned_qty) and status != PlanStatusEnum.COMPLETED.value:
                updates.append({
                    'id' : id,
                    'status' : PlanStatusEnum.COMPLETED.value
                })
        self.repository.bulk_update_plan_status(updates)

    def transform_dict_to_model(self, dict):
        pass

    def transform_model_to_dict(self, sorted_model):
        model: MSILPlan = sorted_model[0]
        model_name = sorted_model[1]
        if sorted_model[5]:
            part_name = sorted_model[2] + "(" + sorted_model[5] + ")"
        else:
            part_name = sorted_model[2]
        material_code = sorted_model[6]
        actual_quantity = sorted_model[7]
        return {
            "machine": sorted_model[4],
            "model": model_name,
            "part_name": part_name,
            "pe_code": sorted_model[3],
            "work_order_no": model.work_order_number,
            "production_date": model.production_date,
            "shift": model.shift,
            "priority": model.priority,
            "planned_qty": model.planned_quantity,
            "actual_qty": actual_quantity or 0,
            "status": model.status.name,
            "material_code": material_code
        }

    def plan_alert(self, notification, shop_id):
        notification_obj = AlertNotification()
        notification_obj.notification = notification
        notification_obj.notification_metadata = None
        notification_obj.alert_type = "Plan Upload Error"
        notification_obj.created_at = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        notification_obj.shop_id = shop_id
        self.msil_alert_repository.add(notification_obj)

    # def alert_if_no_plan_for_today(self):
    #     plan_exists_for_today = self.msil_status_repository.check_if_plan_exists_for_today()
    #     if plan_exists_for_today == False:
    #         ## Check if no plan for a line item but production is on for it.
    #         pass

    def plan_not_created_alert(self, notification, shop_id=None):
        notification_obj = AlertNotification()
        notification_obj.notification = notification
        notification_obj.notification_metadata = None
        notification_obj.alert_type = "Today's plan unavailable"
        notification_obj.created_at = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        notification_obj.shop_id = shop_id
        self.msil_alert_repository.add(notification_obj)

    def update_plan_statuses(self,today):
        try:
            self.repository.update_plan_statuses(today)
            return {"message": "Plan statuses updated successfully"}

        except Exception as e:
            return {"error": str(e)}
