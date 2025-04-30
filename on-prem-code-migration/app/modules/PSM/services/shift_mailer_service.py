from modules.PSM.repositories.msil_variant_repository import MSILVariantRepository
from modules.PSM.repositories.models.msil_variant import MSILVariant
from modules.PSM.repositories.shift_mailer_repository import MSILShiftMailerRepository
from modules.PSM.services.msil_equipment_service import MSILEquipmentService
from modules.PSM.services.service import Service
from modules.PSM.services.msil_report_downtime_service import MSILReportDowntimeService
from modules.PSM.services.shift_util import get_shift,SHIFT_MAPPING_WITH_TIME,get_shift_with_start_end
from modules.PSM.services.msil_telemetry_service import MSILTelemetryService
import xlsxwriter
import datetime
import pytz
import json
import boto3
from xlsxwriter.utility import xl_col_to_name
import json


s3_client = boto3.client('s3')
ist_tz = pytz.timezone('Asia/Kolkata')
todays_date = (datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1))
ist_tz = pytz.timezone('Asia/Kolkata')
class MSILShiftMailerService(Service):

    def __init__(self, equipment_service : MSILEquipmentService,
                 downtime_service:MSILReportDowntimeService,repository : MSILShiftMailerRepository ,telemetry_service : MSILTelemetryService):
        self.equipment_service = equipment_service
        self.downtime_service = downtime_service
        self.telemetry_service = telemetry_service
        self.repository = repository

    def get_shop_view_data(self,shop_id):
        shop_view_data = {}
        data = self.equipment_service.get_shop_view(shop_id,is_mailer=True)
        data = data.get('machine_list',[])
        if data is None:
            data = []
        for each in data:
            shop_view_data[each.get('machine_name','None')] = each
        return shop_view_data
    
    def get_shop_view_data_for_batch(self,shop_id,batch_st,batch_et,machine_name,material_code):
        shop_view_data = {}
        batch_st = batch_st.time() if isinstance(batch_st, datetime.datetime) else batch_st
        batch_et = batch_et.time() if isinstance(batch_et, datetime.datetime) else batch_et
        data = self.equipment_service.get_shop_view(shop_id,is_mailer=True,batch_st=batch_st,batch_et=batch_et,machine_name=machine_name,material_code=material_code)
        data = data.get('machine_list',[])
        if data is None:
            data = []
        for each in data:
            shop_view_data[each.get('machine_name','None')] = each
        return shop_view_data
    
    def extract_fields(self,data, fields):
        result = {}
        if isinstance(data, dict):
            for key, value in data.items():
                if key in fields:
                    result[key] = value
                elif isinstance(value, dict):
                    extracted = self.extract_fields(value, fields)
                    if extracted:
                        result.update(extracted)
        return result

    def get_report_data_for_batch(self,shop_id,batch_st,batch_et,machine_name,model_name,part_name,today):
        today = today.date()
        print("today date  = ",today,type(today))
        # batch_st = datetime.datetime.strptime(str(batch_st), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")
        # batch_et = datetime.datetime.strptime(str(batch_et), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")
        batch_st = batch_st.date()
        batch_et = batch_et.date()
        
        data = self.telemetry_service.get_production_report(shop_id=str(shop_id),
                                                     start_date=today,
                                                     end_date=today,
                                                     machine_list=[machine_name],
                                                     model_list=[model_name],
                                                     part_list=[part_name],
                                                     batch_st=None,
                                                     batch_et=None,
                                                     in_minutes=True)
        fields_to_extract = ['prod_qty', 'idle_duration', 'breakdown_duration', 'SPH', 'efficiency','scheduled_duration','runtime']
        data = self.extract_fields(data[0],fields_to_extract)
        print("report_data = ",data)
        return data
        

    
    
    def get_downtime_by_shop_id(self,shop_id):
        downtime_data = {}
        shift_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)\
              - datetime.timedelta(hours=1)
        shift  = get_shift(shift_datetime.time())
        today = (datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=6)).date()
        data = self.downtime_service.get_downtime_data(shop_id=shop_id,start_date=today,
                                                    end_date=today)
        shift = get_shift((datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).time())
        
        if data is None:
            data = []

        for each in data:

            if each.get('shift '+shift) != None:
                shift_data = each.get('shift '+shift)[0]
                downtime_data[each.get('machine_name','None')] = {
                    'runtime' : shift_data['running_time'],
                    'ideal_time':shift_data['idle_downtime'],
                    'schedule_stop':shift_data['scheduled_downtime'],
                    'stop_time' : shift_data['breakdown_downtime'] 
                }
            else:
                downtime_data[each.get('machine_name','None')] = {
                    'runtime' : None,
                    'ideal_time':None,
                    'schedule_stop':None,
                    'stop_time' : None
                }
                

        return downtime_data
    
    
    def upload_csv_to_s3(self,temporary_file_path,shop_name,bucket):
        report_date_folder = "pressshop_shift_report/"
        report_date_folder = report_date_folder + f"{todays_date.year}/{todays_date.month}/"
        newFileName = temporary_file_path.replace("/tmp/","")
        newFileName = shop_name + newFileName
        print(f"temporary_file_path : {temporary_file_path}")
        print(f"newFileName : {newFileName}")
        # try:
        response = s3_client.upload_file(temporary_file_path, bucket,report_date_folder + newFileName)
        object_url = "https://"+bucket+".s3.ap-south-1.amazonaws.com/" + report_date_folder + newFileName
        return object_url
        # except ClientError as e:
        #     print(e)
            
    def get_alerts(self,shop_id):
        curreny_date = (datetime.datetime.now(ist_tz) - datetime.timedelta(hours=1)).date()
        timestamp = (datetime.datetime.now(ist_tz) - datetime.timedelta(hours=1)).time()
        for each_shift in SHIFT_MAPPING_WITH_TIME:
            if each_shift[0] <= timestamp <= each_shift[1]:
                shift = SHIFT_MAPPING_WITH_TIME.get(each_shift)
                print('current_shift = ',shift)
                self.shift_start_time = each_shift[0]
                self.shift_end_time = each_shift[1]
        
        alert_data = self.repository.get_alerts_by_shop_id(shop_id=shop_id,\
                                                   start_time=str(curreny_date)+ ' '+str(self.shift_start_time),\
                                                    end_time=str(curreny_date)+ ' '+str(self.shift_end_time))
        data = []
        for each in alert_data:
            data.append([
                each.notification,
                each.created_at,
                each.alert_type
            ])
        return data
    
    def shift_mailer_job(self,shop_id,shop_name,bucket):
        data = []
        shop_view_data = self.get_shop_view_data(shop_id=shop_id)
        downtime_data = self.get_downtime_by_shop_id(shop_id=shop_id)
        target_data = self.get_target_values_shop_id(shop_id=shop_id)
        alert_data = self.get_alerts(shop_id=shop_id)
        
        for each in shop_view_data.keys():
            target_percent = 100
            try:
                if shop_view_data.get(each, {}).get('target', 0) != 0:
                    target_percent = (float(shop_view_data.get(each, {}).get('actual', 0)) / float(shop_view_data.get(each, {}).get('target'))) * 100
                else:
                    target_percent = 100  # or any default value you'd like when target is 0
            except (KeyError, TypeError, ZeroDivisionError) as e:
                # Handle or log the exception
                print(f"An error occurred: {e}")
            if target_percent > 100:
                target_percent = 100
            actual_max = 0
            try : 
                if shop_view_data.get(each,{}).get('actual_max',0) :
                    actual_max = shop_view_data.get(each,{}).get('actual_max',0)
            except Exception as e:
                print(f"An error occurred: {e}")

            data.append(
                [each,                                                                                  #1 target stroke
                 target_data.get(each,{}).get('strokes'),                                               #2 strokes actual
                 shop_view_data.get(each,{}).get('actual_max',0),                                             #3 strokes difference
                 actual_max- target_data.get(each,{}).get('strokes',0) ,     #4 target sph
                 int(target_data.get(each,{}).get('sph',0)),                                                   #5 actual sph
                 int(shop_view_data.get(each,{}).get('sph',0)),                                         #6 target efficiency
                 target_data.get(each,{}).get('efficiency'),                                            #7 actual efficiency
                 shop_view_data.get(each,{}).get('efficiency'),                                         #8 plannned qty
                 int(shop_view_data.get(each,{}).get('target')),                                             #9 actual qty
                 shop_view_data.get(each,{}).get('actual'),                                             #10 achivemnet percnet
                 target_percent,                                                                        #11 runtime
                 downtime_data.get(each,{}).get('runtime',None),                                        #12 stop time 
                 downtime_data.get(each,{}).get('stop_time',None),                                      #13 schedule stop
                 downtime_data.get(each,{}).get('schedule_stop',None),                                  #14 idle time
                 downtime_data.get(each,{}).get('ideal_time',None)
                 ]
            )
        file_path = self.generate_production_log_sheet_report(shop_id=shop_id,shop_name=shop_name,data=data,alert_data=alert_data)
        object_url = self.upload_csv_to_s3(file_path,shop_name,bucket)
        return object_url
        
        

    def get_target_values_shop_id(self,shop_id):
        target_data = {}
        data = self.repository.get_target_values_shop_id(shop_id=shop_id)
        for each in data:
            target_data[each.name] = {
                'name' : each.name,
                'efficiency' : each.efficiency,
                'sph' : each.efficiency,
                'strokes' : each.efficiency
            }

        return target_data



    def system_log_sheet_mailer_job(self,shop_id,shop_name,bucket):
        shift_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)\
              - datetime.timedelta(hours=1)
        shift,shift_start_time,shift_end_time  = get_shift_with_start_end(shift_datetime.time())
        shift_start_time = datetime.datetime.combine(shift_datetime.date(),shift_start_time)
        shift_end_time = datetime.datetime.combine(shift_datetime.date(),shift_end_time)
        print("shift = ",shift)
        print("shift_start_time =",shift_start_time)
        print("shift_end_time =",shift_end_time)
        batch_data = self.get_production_log_sheet_data(shop_id=shop_id,
                                                        shift_start_time=shift_start_time,
                                                        shift_end_time=shift_end_time)
        print("got batch data",batch_data)
        downtime_data = self.get_downtime_data_for_production_log_sheet(shop_id=shop_id,
                                                        shift_start_time=shift_start_time,
                                                        shift_end_time=shift_end_time)
        file_path = self.generate_system_log_sheet(shop_id=shop_id,shop_name=shop_name,batch_data=batch_data,downtime_data=downtime_data)
        object_url = self.upload_csv_to_s3(file_path,shop_name,bucket)
        return object_url    


    def get_downtime_data_for_production_log_sheet(self,shop_id,
                                                        shift_start_time,
                                                        shift_end_time):
        data = self.repository.get_downtime_data_for_production_log_sheet(shop_id=shop_id,
                                                                          shift_start_time=shift_start_time,
                                                                          shift_end_time=shift_end_time)
        transform_data = self.transform_downtime_data(data)
        return transform_data

    def transform_downtime_data(self,data):
        downtime_arr = []
        for each in data:
            equipment_obj = self.get_downtime_equipment_obj(downtime_arr,each.equipment_id,each.equipment_name)
            part_obj = self.get_downtime_part_obj(equipment_obj.get('part_arr',[]),each.part_name,each.part_id)
            group_obj = self.get_downtime_group_obj(part_obj.get('downtime_group'),each.part_name)
            group_obj['reason_arr'].append({
                'reason' : each.reason,
                'duration' : float(each.duration)
            })
            part_obj['total'] = float(part_obj['total']) + float(each.duration)
        return downtime_arr
 

    def get_downtime_equipment_obj(self,downtime_arr,equipment_id,equipment_name):
        if len(downtime_arr) > 0 and downtime_arr[-1].get('equipment_id') == equipment_id:
            obj = downtime_arr[-1]
        else:
            obj = {
                'equipment_id' : equipment_id,
                'equipment_name' : equipment_name,
                'part_arr' : [],
                'total' : 0
            }
            downtime_arr.append(obj)
        return obj
    
    def get_downtime_part_obj(self,part_arr,material_code,part_name):
        if len(part_arr) > 0 and part_arr[-1].get('material_code') == material_code:
            obj = part_arr[-1]
        else:
            obj = {
                'material_code' : material_code,
                'part_name' : part_name,
                'downtime_group' : [],
                "total" : 0
            }
            part_arr.append(obj)
        return obj
    
    def get_downtime_group_obj(self,downtime_group,reason_type):
        if len(downtime_group) > 0 and downtime_group[-1].get('reason_type') == reason_type:
            obj = downtime_group[-1]
        else:
            obj = {
                'reason_type' : reason_type,
                'reason_arr' : []
            }
            downtime_group.append(obj)
        return obj
    


    def get_production_log_sheet_data(self,shop_id,shift_start_time,shift_end_time):
        equipment_id_arr,equipment_arr = self.repository.get_equipment_id_by_shop_id(shop_id=shop_id)
        print("equipment_arr = ",equipment_id_arr,equipment_arr)
        batch_data = self.repository.get_system_log_sheet_data(shop_id=shop_id,
                                                  equipment_id=equipment_id_arr,
                                                  shift_start_time=shift_start_time,
                                                  shift_end_time=shift_end_time)
        transformed_data = self.transform_batch_data(batch_data)
        return transformed_data
    
    # def get_production_log_sheet_data(self,shop_id):
        # shift_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)\
        #       - datetime.timedelta(hours=1)
        # shift,shift_start_time,shift_end_time  = get_shift_with_start_end(shift_datetime.time())
        # shift_start_time = datetime.datetime.combine(shift_datetime.date(),shift_start_time)
        # shift_end_time = datetime.datetime.combine(shift_datetime.date(),shift_end_time)
        # print("shift_start_time = ",shift_start_time)
        # print("shift_end_time = ",shift_end_time)
        
        # equipment_id_arr,equipment_arr = self.repository.get_equipment_id_by_shop_id(shop_id=shop_id)
        # batch_data = self.repository.get_system_log_sheet_data(shop_id=shop_id,
        #                                           equipment_id=equipment_id_arr,
        #                                           shift_start_time=shift_start_time,
        #                                           shift_end_time=shift_end_time)
        
        # transformed_data = self.transform_batch_data(batch_data)
        # print("transformed_data = ",transformed_data)
        # return None
        # # return transformed_data




    def transform_batch_data(self,data):
        equipment_arr = []
        for each in data :
            equiment_obj = self.get_msil_equipment_obj(equipment_arr=equipment_arr,
                                        equipment_id=each.equipment_id,
                                        equipment_name=each.equipment_name)
            
            batch_obj = self.get_batch_obj(equiment_obj['batch_arr'],each.batch_id,each)
            if each.reject_qty == None:
                batch_obj['rework_qty'] = batch_obj['rework_qty'] + each.rework_qty if  each.rework_qty else 0
                batch_obj['rework_reason'].append(each.remark)
            
            if each.rework_qty == None:
                batch_obj['reject_qty'] = batch_obj['reject_qty'] + each.reject_qty if  each.reject_qty else 0
                batch_obj['reject_reason'].append(each.remark)
                
        return equipment_arr

                            
                        


    def get_batch_obj(self,batch_arr,batch_id,data):
        if len(batch_arr) > 0 and batch_arr[-1].get('batch_id') == batch_id:
            obj = batch_arr[-1]
        else:
            # batch_st = data.start_time.time() if isinstance(data.start_time, datetime.datetime) else data.start_time
            # batch_et = data.end_time.time() if isinstance(data.end_time, datetime.datetime) else data.end_time
            # shop_view_data = self.get_shop_view_data_for_batch(shop_id=data.shop_id,batch_st=data.start_time,batch_et=data.end_time,machine_name=[data.equipment_name],material_code=data.material_code)
            report_data = self.get_report_data_for_batch(shop_id=data.shop_id,batch_st=data.start_time,batch_et=data.end_time,machine_name=data.equipment_name,model_name=data.model_name,part_name=data.part_name,today=todays_date)
            efficiency = 0
            try:
                efficiency = report_data.get('efficiency',0)
            except Exception as e:
                print(f"An error occurred: {e}")

            sph = 0
            try:
                sph = int(report_data.get('SPH',0))
            except Exception as e:
                print(f"An error occurred: {e}")
            downtime = 0
            try:
                downtime = (
                    float(report_data.get('breakdown_duration', 0)) +
                    float(report_data.get('scheduled_duration', 0)) +
                    float(report_data.get('idle_duration', 0))
                )
            except Exception as e:
                print(f"An error occurred: {e}")


            obj = {
                'batch_id' : data.batch_id,
                'model_name' : data.model_name,
                'variant_name' : data.variant_name,
                'pe_code' : data.pe_code,
                'part_name' : data.part_name,
                'production_qty' : data.quantity,
                'material_id' : data.material_id,
                'start_time' : data.start_time,
                'end_time' : data.end_time,
                'specs' : {
                    'thickness' : data.thickness,
                    'width' : data.width,
                    'material_qty' : data.material_qty
                },
                'details' : data.details,
                'efficiency' : efficiency,
                'sph' : sph,
                'SPM' : data.SPM,
                'downtime' : downtime,
                'runtime' : str(data.end_time-data.start_time),
                'rework_qty' : 0,
                'reject_qty' : 0,
                'reject_reason' : [],
                'rework_reason' : []
            }
            batch_arr.append(obj)

        return obj

    def get_msil_equipment_obj(self,equipment_arr,equipment_id,equipment_name):
        if len(equipment_arr) > 0 and equipment_arr[-1].get('equipment_id') == equipment_id:
            obj = equipment_arr[-1]
        else:
            obj = {
                'equipment_id' : equipment_id,
                'equipment_name' : equipment_name,
                'batch_arr' : []
            }
            equipment_arr.append(obj)
        return obj

    
    def generate_production_log_sheet_report(self,shop_id, shop_name,data = [],alert_data=[]):
        # Define the name of the Excel workbook
        shift = get_shift((datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).time())
        today = (datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).date()
        WORKBOOK_NAME = "/tmp/" + "production_summary_prodigi_shift_mailer_for_" + shop_name +"_"+ str(today)+"_"+shift+ ".xlsx"

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(WORKBOOK_NAME)

        # Create formatting for merged cells
        merge_format1 = workbook.add_format({
            'bold': True,
            'border': 1,
            'valign': 'vcenter',
            'font_size': 16
        })
        merge_format2 = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 24
        })
        merge_format3 = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16
        })

        cell_format = workbook.add_format({
            'font_size': 12,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',  # Ensures vertical alignment in the center
            'text_wrap': True  # Enables text wrapping inside the cell
        })
        
        cell_format2 = workbook.add_format({
            'font_size': 12,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
             'text_wrap': True # Enables text wrapping inside the cell
        })

        # Add a new worksheet to the workbook
        worksheet = workbook.add_worksheet(name='Production Log Sheet')
        shop_name = "SHOP NAME : " + shop_name  
        timestamp = (datetime.datetime.now(ist_tz) - datetime.timedelta(hours=1))
        today = str(timestamp.date())
        Date = "Date : " + today
        Shift = "Shift : " + get_shift((datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).time())
        Group = "Group : "

        # Merge cells and apply the formatting
        worksheet.merge_range('B1:H1', "MARUTI SUZUKI INDIA LIMITED", merge_format2)
        worksheet.merge_range('I1:P1', shop_name, merge_format2)
        worksheet.merge_range('A1:A2', "", merge_format1)
        worksheet.merge_range('B2:C2', Date, merge_format1)
        worksheet.merge_range('D2:E2', Shift, merge_format1)
        worksheet.merge_range('F2:H2', Group, merge_format1)
        worksheet.merge_range('I2:P2', "", merge_format1)
        worksheet.merge_range('A3:P3', "SHOP OPERATION ANALYSIS REPORT", merge_format3)
        worksheet.merge_range('A4:B4',"Machine List",cell_format)
        worksheet.merge_range('C4:E4',"STROKES",cell_format)
        worksheet.merge_range('F4:G4',"SPH",cell_format)
        worksheet.merge_range('H4:I4',"Efficiency",cell_format)
        worksheet.merge_range('J4:L4',"Production",cell_format)
        worksheet.merge_range('M4:P4',"Time Analysis (mins)",cell_format)
        


        # Assuming headings_1 and worksheet are already defined
        headings_1 = [
            "S No.", "Machine", "Target", "Actual", "Difference", "Target SPH", "Actual SPH",
            "Target", "Actual", "Planned Quantity", "Actual Quantity", "Achievement %",
            "Run Time", "Stop Time", "Scheduled Stop", "Idle Time"
        ]

        for col_num, header in enumerate(headings_1):
            worksheet.write(4, col_num, header, cell_format) 


        merge_format4 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
            'bg_color': '#FFAF7A',  # Example color: yellow
            'pattern': 1  # Solid fill pattern
        })


       


        serial_number = 1

        # Insert serial numbers and write data
        for each in data:
            each.insert(0, serial_number)  # Insert serial number at the start
            for col_num, value in enumerate(each):
                worksheet.write(4 + serial_number, col_num, value, cell_format)
            serial_number += 1

        row_number = 5 + serial_number
        worksheet.merge_range(f'A{str(row_number)}:P{str(row_number)}', "ALERTS", merge_format4)
        headings_2 = ['S No.', 'Description', 'Time','Alert Type','','','','','','','','','','','','']
        row_number += 1
        
        serial_number = 1  
        for col_num, header in enumerate(headings_2):
            worksheet.write(row_number, col_num, header, cell_format)
        row_number += 1 
        for each in alert_data:
            each.insert(0, serial_number+1)  # Insert serial number at the start
            for col_num, value in enumerate(each):
                worksheet.write(row_number + serial_number, col_num, str(value), cell_format2)
                worksheet.set_row(row_number + serial_number, height=30)
            serial_number += 1


        # Close the workbook to save the changes
        workbook.close()

        print(f"Workbook '{WORKBOOK_NAME}' created successfully.")
        
        return WORKBOOK_NAME

    def generate_system_log_sheet(self,shop_id,shop_name,batch_data,downtime_data):
        machine_list = []
        machine_list.append({
            'machine_id' : 1,
            'machine_name' : 'Machine 1'
        })
        machine_list.append({
            'machine_id' : 2,
            'machine_name' : 'Machine 2'
        })
        # Define the name of the Excel workbook
        shift = get_shift((datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).time())
        today = (datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).date()
        print("shift in logsheet",shift)
        WORKBOOK_NAME = "/tmp/" + "system_logsheet_prodigi_shift_mailer_for_" + shop_name +"_"+ str(today)+"_"+shift+ ".xlsx"

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(WORKBOOK_NAME)
        # Create formatting for merged cells
        merge_format1 = workbook.add_format({
            'bold': True,
            'border': 1,
            'valign': 'vcenter',
            'font_size': 16
        })
        merge_format2 = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 24
        })
        cell_format = workbook.add_format({
                'font_size': 12,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',  # Ensures vertical alignment in the center
                'text_wrap': True  # Enables text wrapping inside the cell
            })


        for each in batch_data:
            machine_id = each.get('equipment_id')
            machine_name = each.get('equipment_name')
            batch_arr = each.get('batch_arr')
            worksheet = workbook.add_worksheet(machine_name)
            shop_name = "SHOP NAME : " + shop_name  
            timestamp = (datetime.datetime.now() - datetime.timedelta(hours=1))
            worksheet.set_column('A:Z', 25)
            today = str(timestamp.date())
            Date = "Date : " + today
            Shift = "Shift : " + get_shift((datetime.datetime.now(ist_tz).replace(tzinfo=None)\
                 - datetime.timedelta(hours=1)).time())
            Group = "Group : "
            machine_name_str = "Machine Name : " + machine_name
            worksheet.merge_range('B1:N1', "MARUTI SUZUKI INDIA LIMITED", merge_format2)
            worksheet.merge_range('O1:W1', shop_name, merge_format2)
            worksheet.write('A2', "", merge_format1)
            worksheet.write('B2', "", merge_format1)
            worksheet.write('A3', "", merge_format1)
            worksheet.merge_range('C2:D2', Date, merge_format1)
            worksheet.merge_range('E2:F2', Shift, merge_format1)
            worksheet.merge_range('G2:I2', Group, merge_format1)
            worksheet.merge_range('J2:Y2', machine_name_str, merge_format1)
            worksheet.merge_range('B3:L3','Production Report',self.get_merge_format(workbook=workbook,
                                                                            allign='center',
                                                                            valign='vcenter',
                                                                            font_size=24,
                                                                            bg_color='#C6E0B4',
                                                                            pattern=1))
            worksheet.merge_range('M3:T3','Operation Analysis',self.get_merge_format(workbook=workbook,
                                                                    allign='center',
                                                                    valign='vcenter',
                                                                    font_size=24,
                                                                    bg_color='#F4B084',
                                                                    pattern=1))

            worksheet.merge_range('U3:W3','Traceability',self.get_merge_format(workbook=workbook,
                                                                    allign='center',
                                                                    valign='vcenter',
                                                                    font_size=24,
                                                                    bg_color='#FFE699',
                                                                    pattern=1))
        
            headers_1 = [
                "S No.", "Model*", "Variant", "PE Code*", "Part Name*", "Production Qty*", 
                "Rejected Qty", "Rejection Reason", "Rework Qty", "Rework Reason", "Start Time*", 
                "End Time*", "Run Time*", "Downtime*", "Efficiency*", "SPH*", 
                "SPM/Cycle Time", "Group 1 Duration", "Group 2 Duration", "Group 3 Duration", 
                "Input Material Id", "Input material spec", "Details of output handling unit"
            ]
            worksheet.set_row(4, 35)

            for col_num, header in enumerate(headers_1):
                worksheet.write(4, col_num, header, self.get_merge_format(workbook=workbook,
                                                                    allign='center',
                                                                    valign='vcenter',
                                                                    font_size=16)) 
            serial_number = 1
            for each in batch_arr:
                start_time = each.get('start_time', None)
                if start_time:
                    # Convert the string to a datetime object and reformat it
                    formatted_start_time = datetime.datetime.fromisoformat(str(start_time)).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    formatted_start_time = None
                end_time = each.get('end_time', None)
                if end_time:
                    # Convert the string to a datetime object and reformat it
                    formatted_end_time = datetime.datetime.fromisoformat(str(end_time)).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    formatted_end_time = None

                runtime = each.get('runtime', None)
                # Check if runtime is not None and format it
                if runtime:
                    # Calculate the runtime as a timedelta
                    runtime_delta = each.get('end_time') - each.get('start_time')

                    # Extract total seconds
                    total_seconds = int(runtime_delta.total_seconds())

                    # Format the runtime in HH:MM:SS format
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    # Format as HH:MM:SS
                    formatted_runtime = f"{hours:02}:{minutes:02}:{seconds:02}"
                else:
                    formatted_runtime = None

                    
                worksheet.write(4+serial_number,0,serial_number,cell_format)
                worksheet.write(4+serial_number,1,each.get('model_name',None),cell_format)
                worksheet.write(4+serial_number,2,each.get('variant_name',None),cell_format)
                worksheet.write(4+serial_number,3,each.get('pe_code',None),cell_format)
                worksheet.write(4+serial_number,4,each.get('part_name',None),cell_format)
                worksheet.write(4+serial_number,5,each.get('production_qty',None),cell_format)
                worksheet.write(4+serial_number,6,each.get('reject_qty',None),cell_format)
                worksheet.write(4+serial_number,7,json.dumps(each.get('reject_reason',None)),cell_format)
                worksheet.write(4+serial_number,8,each.get('rework_qty',None),cell_format)
                worksheet.write(4+serial_number,9,json.dumps(each.get('rework_reason',None)),cell_format)
                worksheet.write(4+serial_number,10,formatted_start_time,cell_format)
                worksheet.write(4+serial_number,11,formatted_end_time,cell_format)
                worksheet.write(4+serial_number,12,formatted_runtime,cell_format)
                worksheet.write(4+serial_number,13,each.get('downtime',None),cell_format)
                worksheet.write(4+serial_number,14,round(each.get('efficiency', 0), 2),cell_format)
                worksheet.write(4+serial_number,15,int(each.get('sph',0)),cell_format)
                worksheet.write(4+serial_number,16,each.get('SPM',None),cell_format)
                worksheet.write(4+serial_number,17,"",cell_format)
                worksheet.write(4+serial_number,18,"",cell_format)
                worksheet.write(4+serial_number,19,"",cell_format)
                worksheet.write(4+serial_number,20,each.get('material_id',None),cell_format)
                worksheet.write(4+serial_number,21,str(each.get('specs',None)),cell_format)
                worksheet.write(4+serial_number,22,each.get('details',None),cell_format)
                serial_number +=1
            

            row_number = 4 + serial_number+2
            worksheet.merge_range(f'A{str(row_number+2)}:W{str(row_number+1)}', "Machine Breakdown Report",                 
                                                                    self.get_merge_format(workbook=workbook,
                                                                    allign='center',
                                                                    valign='vcenter',
                                                                    font_size=27,
                                                                    bg_color='#F4B084',
                                                                    pattern=1))
            row_number = row_number + 1


            for dt_each in downtime_data:
                if dt_each.get('equipment_name',None) == machine_name:
                    for pt_each in dt_each.get('part_arr'):
                        row_number = self.get_downtime_header(worksheet,row_number,pt_each,cell_format)
                else:
                    pass




            


            

        workbook.close()

        print(f"Workbook '{WORKBOOK_NAME}' created successfully.") 
        return WORKBOOK_NAME   

    def get_downtime_header(self,worksheet,row_number,data,cell_format):
        current_col = 2
        temp_col = 2
        row_number = row_number+2
        worksheet.merge_range(f'A{row_number}:A{row_number+1}', "Material Code", cell_format)
        worksheet.merge_range(f'B{row_number}:B{row_number+1}', "Part Name*", cell_format)
        worksheet.write(f'A{row_number+2}', data.get("part_name"), cell_format)
        worksheet.write(f'B{row_number+2}', data.get("material_code"), cell_format)
        
        downtime_group_arr = data.get("downtime_group")        
        for dt_group in downtime_group_arr:
            reason_arr = dt_group.get("reason_arr")
            reason_len = len(reason_arr)
            end_col = current_col + (2 * reason_len) - 1
            start_col_letter = xl_col_to_name(current_col)
            end_col_letter = xl_col_to_name(end_col)
            worksheet.merge_range(f'{start_col_letter}{row_number}:{end_col_letter}{row_number}',dt_group.get('reason_type',""),cell_format)
            for count in range(current_col,end_col+1):
                temp_row_number = row_number+1
                if count%2 == 0:
                    worksheet.write(f'{xl_col_to_name(count)}{temp_row_number}', "Reason", cell_format)
                else:
                    worksheet.write(f'{xl_col_to_name(count)}{temp_row_number}', "Duration (mins)", cell_format)
            count = current_col
            for reason in reason_arr:
                temp_row_number = row_number+2
                if count%2 == 0:
                    downtime_seconds = reason.get('duration',0) * 60
                    downtime_minutes = downtime_seconds // 60
                    remaining_seconds = (downtime_seconds % 60) / 100.0
                    downtime_duration = downtime_minutes + round(remaining_seconds, 2)
                    worksheet.write(f'{xl_col_to_name(count)}{temp_row_number}', reason.get('reason',None), cell_format)
                    worksheet.write(f'{xl_col_to_name(count+1)}{temp_row_number}', downtime_duration, cell_format)
                else:
                    downtime_seconds = reason.get('duration',0) * 60
                    downtime_minutes = downtime_seconds // 60
                    remaining_seconds = (downtime_seconds % 60) / 100.0
                    downtime_duration = downtime_minutes + round(remaining_seconds, 2)
                    worksheet.write(f'{xl_col_to_name(count)}{temp_row_number}', reason.get('duration',None), cell_format)
                    worksheet.write(f'{xl_col_to_name(count)}{temp_row_number}', downtime_duration, cell_format)
                count = count+2
                

            current_col = end_col + 1
        worksheet.merge_range(f'{xl_col_to_name(current_col)}{row_number}:{xl_col_to_name(current_col)}{row_number+1}', "Total Downtime ", cell_format)
        downtime_seconds = data.get('total',0) * 60
        downtime_minutes = downtime_seconds // 60
        remaining_seconds = (downtime_seconds % 60) / 100.0
        downtime_duration = downtime_minutes + round(remaining_seconds, 2)
        worksheet.write(f'{xl_col_to_name(current_col)}{row_number+2}', downtime_duration, cell_format)

        return row_number+4

    def get_merge_format(self,workbook,allign=None,valign=None,font_size=12,
                        bg_color=None,pattern=1,bold=1,border=1):
        obj = {}
        if allign:
            obj['align'] = allign
        
        if valign:
            obj['valign'] = valign
        
        if bg_color:
            obj['bg_color'] = bg_color
            obj['pattern'] = pattern

        obj['font_size'] = font_size 
        obj['bold'] = bold

        if border:
            obj['border'] = border

        obj['text_wrap'] = True

        return workbook.add_format(obj)

