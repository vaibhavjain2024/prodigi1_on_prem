import pytz
from .repository import Repository
from modules.PSM.repositories.msil_telemetry_repository import MSILTelemetryRepository
from .models.msil_downtime import MSILDowntime
from .models.msil_downtime_reason import MSILDowntimeReasons
from .models.msil_downtime_remark import MSILDowntimeRemarks
from .models.msil_equipment import MSILEquipment
from .models.msil_model import MSILModel
from .models.msil_shift import MSILShift
from .models.msil_shop_breaks import MSILShopBreaks
from .models.msil_part import MSILPart
from collections import defaultdict
from datetime import date
from sqlalchemy import (
    extract,
    func,
    desc,
    case,
    and_,
    cast,
    Date
)
from sqlalchemy.orm import Session
import datetime
ist_tz = pytz.timezone('Asia/Kolkata')
from modules.PSM.services.shift_util import get_shift

class MSILReportDowntimeRepository(Repository):
    """

    """

    def __init__(self,session:Session):
        self.session = session
        self.model_type = MSILDowntime
        self.remark_model = MSILDowntimeRemarks
    
    
    def get_runtime_by_shift(self, shifts_list):
                with self.session:
                    shifts = shifts_list
                    shift_obj = {}
                    for shift in shifts:
                        shift_start = shift.shift_start_timing
                        shift_end = shift.shift_end_timing
                        shift_obj[shift.shift_name] = {
                            "runtime" : (datetime.datetime.combine(date.today(),shift_end) 
                                         - datetime.datetime.combine(date.today(),shift_start)) 

                        }
                    # print("runtime",shift_obj)
                    return shift_obj
                

    def get_downtime_data(self, shop_id, start_date, end_date,shifts_list,first_shift_time,machine_list = None,
                                 model_list=None, part_name_list = None, shift = None):
        
        number_of_days = (end_date - start_date).days + 1

        def date_range(start_date, end_date):   
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += datetime.timedelta(days=1)
            return date_list
        days = date_range(start_date , end_date)
        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz)
        cur_time = cur_datetime.time()
        cur_date = datetime.date.today()
        print("first_shift_time2 = ",first_shift_time)
        with self.session:
            start = first_shift_time
            print("start = ",start)
            start_timedelta = datetime.timedelta(hours=start.hour,minutes=start.minute)
            print("shifts_list",shifts_list)
            shift_duration = self.get_runtime_by_shift(shifts_list)
            print("shift_duration",shift_duration)

            idle_downtime_query = self.session.query(
                MSILEquipment.name.label("Equipment_name"),
                self.model_type.shift.label("Shift"),
                self.model_type.duration.label("Idle_hours"),
                cast(MSILDowntime.start_time - start_timedelta,Date).label('Downtime_date'),
                 MSILDowntimeReasons.reason.label("Idle_downtime_reasons")
                
                ) \
            .select_from(self.model_type) \
            .join(MSILEquipment, MSILEquipment.id == MSILDowntime.equipment_id) \
            .join(MSILDowntimeReasons, MSILDowntimeReasons.id == MSILDowntime.reason_id) \
            .filter(and_(MSILEquipment.shop_id == shop_id,
                MSILDowntimeReasons.reason_type == 'idle')) \
            .filter(MSILEquipment.is_deleted == False)
            
            if(shift):
                idle_downtime_query = idle_downtime_query.filter(MSILDowntime.shift.in_(shift))
                
            idle_downtime_query = idle_downtime_query.join(MSILPart, self.model_type.material_code == MSILPart.material_code,isouter=True) 

            idle_downtime_query = idle_downtime_query.join(MSILModel, MSILPart.model_id == MSILModel.id,isouter=True)
            
            if(model_list):
                idle_downtime_query = idle_downtime_query.filter(MSILModel.model_name.in_(model_list))
                        
            if(part_name_list):
                idle_downtime_query = idle_downtime_query.filter(MSILPart.part_name.in_(part_name_list))   
            
            if(machine_list):
                idle_downtime_query = idle_downtime_query.filter(MSILEquipment.name.in_(machine_list))

            idle_downtime_query = idle_downtime_query.subquery()

            idle_query = self.session.query(
                idle_downtime_query.c.Equipment_name,
                idle_downtime_query.c.Shift,
                func.coalesce(func.sum(idle_downtime_query.c.Idle_hours)/number_of_days,0),
                idle_downtime_query.c.Downtime_date,
                idle_downtime_query.c.Idle_downtime_reasons
            
            ) \
            .filter(idle_downtime_query.c.Downtime_date.in_(days)  ) \
            .group_by(idle_downtime_query.c.Downtime_date,
                      idle_downtime_query.c.Equipment_name,
                      idle_downtime_query.c.Shift,
                      idle_downtime_query.c.Idle_downtime_reasons,
                      ) \
            .all()
           
            breakdown_downtime_query = self.session.query(
                MSILEquipment.name.label("Breakdown_equipment_name"),
                self.model_type.shift.label("Breakdown_shift"),
                self.model_type.duration.label("Breakdown_hours"),
                cast(MSILDowntime.start_time - start_timedelta,Date).label('Downtime_date'),
                MSILDowntimeReasons.reason.label("Breakdown_downtime_reasons")
                
            ) \
            .select_from(self.model_type) \
            .join(MSILEquipment, MSILEquipment.id == MSILDowntime.equipment_id) \
            .join(MSILDowntimeReasons, MSILDowntimeReasons.id == MSILDowntime.reason_id) \
            .filter(and_(
                MSILEquipment.shop_id == shop_id,
                MSILDowntimeReasons.reason_type == 'breakdown'
            )) \
            .filter(MSILEquipment.is_deleted == False)

            if(shift):
                breakdown_downtime_query = breakdown_downtime_query.filter(MSILDowntime.shift.in_(shift))
                
            breakdown_downtime_query = breakdown_downtime_query.join(MSILPart, self.model_type.material_code == MSILPart.material_code,isouter=True) 

            breakdown_downtime_query = breakdown_downtime_query.join(MSILModel, MSILPart.model_id == MSILModel.id,isouter=True)
            
            if(model_list):
                breakdown_downtime_query = breakdown_downtime_query.filter(MSILModel.model_name.in_(model_list))
                        
            if(part_name_list):
                breakdown_downtime_query = breakdown_downtime_query.filter(MSILPart.part_name.in_(part_name_list))   
            
            if(machine_list):
                breakdown_downtime_query = breakdown_downtime_query.filter(MSILEquipment.name.in_(machine_list))
            
            breakdown_downtime_query = breakdown_downtime_query.subquery()

            breakdown_query = self.session.query(
                breakdown_downtime_query.c.Breakdown_equipment_name,
                breakdown_downtime_query.c.Breakdown_shift,
                func.coalesce(func.sum(breakdown_downtime_query.c.Breakdown_hours)/number_of_days,0),
                breakdown_downtime_query.c.Downtime_date,
                breakdown_downtime_query.c.Breakdown_downtime_reasons
                
            ) \
            .filter(breakdown_downtime_query.c.Downtime_date.in_(days)) \
            .group_by(breakdown_downtime_query.c.Downtime_date,
                breakdown_downtime_query.c.Breakdown_equipment_name,
                breakdown_downtime_query.c.Breakdown_shift,
                breakdown_downtime_query.c.Breakdown_downtime_reasons) \
            .all()

            scheduled_downtime_query = self.session.query(
                MSILEquipment.name.label("Equipment_name"),
                self.model_type.shift.label("Shift"),
                self.model_type.duration.label("Scheduled_hours"),
                cast(MSILDowntime.start_time - start_timedelta,Date).label('Downtime_date'),
                 MSILDowntimeReasons.reason.label("Scheduled_downtime_reasons")
                
                ) \
            .select_from(self.model_type) \
            .join(MSILEquipment, MSILEquipment.id == MSILDowntime.equipment_id) \
            .join(MSILDowntimeReasons, MSILDowntimeReasons.id == MSILDowntime.reason_id) \
            .filter(and_(MSILEquipment.shop_id == shop_id,
                MSILDowntimeReasons.reason_type == 'scheduled')) \
            .filter(MSILEquipment.is_deleted == False)
            
            if(shift):
                scheduled_downtime_query = scheduled_downtime_query.filter(MSILDowntime.shift.in_(shift))
                
            scheduled_downtime_query = scheduled_downtime_query.join(MSILPart, self.model_type.material_code == MSILPart.material_code,isouter=True) 

            scheduled_downtime_query = scheduled_downtime_query.join(MSILModel, MSILPart.model_id == MSILModel.id,isouter=True)
            
            if(model_list):
                scheduled_downtime_query = scheduled_downtime_query.filter(MSILModel.model_name.in_(model_list))
                        
            if(part_name_list):
                scheduled_downtime_query = scheduled_downtime_query.filter(MSILPart.part_name.in_(part_name_list))   
            
            if(machine_list):
                scheduled_downtime_query = scheduled_downtime_query.filter(MSILEquipment.name.in_(machine_list))

            scheduled_downtime_query = scheduled_downtime_query.subquery()

            scheduled_query = self.session.query(
                scheduled_downtime_query.c.Equipment_name,
                scheduled_downtime_query.c.Shift,
                func.coalesce(func.sum(scheduled_downtime_query.c.Scheduled_hours)/number_of_days,0),
                scheduled_downtime_query.c.Downtime_date,
                scheduled_downtime_query.c.Scheduled_downtime_reasons
            
            ) \
            .filter(scheduled_downtime_query.c.Downtime_date.in_(days)  ) \
            .group_by(scheduled_downtime_query.c.Downtime_date,
                      scheduled_downtime_query.c.Equipment_name,
                      scheduled_downtime_query.c.Shift,
                      scheduled_downtime_query.c.Scheduled_downtime_reasons,
                      ) \
            .all()
            
            idle_results = idle_query
            breakdown_results = breakdown_query
            scheduled_results = scheduled_query
            
        merged_idle_data = defaultdict(lambda: defaultdict(lambda: {
            'name': '',
            'Total_Working_time': 0,
            'Idle_downtime': 0,
            'Downtime_count': 0,
            'reasons': defaultdict(int)
        }))

        merged_breakdown_data = defaultdict(lambda: defaultdict(lambda: {
            'name': '',
            'Total_Working_time': 0,
            'Breakdown_downtime': 0,
            'Downtime_count': 0,
            'reasons': defaultdict(int)
        }))

        merged_scheduled_data = defaultdict(lambda: defaultdict(lambda: {
            'name': '',
            'Total_Working_time': 0,
            'Scheduled_downtime': 0,
            'Downtime_count': 0,
            'reasons': defaultdict(int)
        }))
        
        for result in idle_results:
            equipment_name, shift, idle_hours, downtime_date, downtime_reason = result
            merged_idle_data[equipment_name][shift]['name'] = shift
            merged_idle_data[equipment_name][shift]['Idle_downtime'] += idle_hours
            merged_idle_data[equipment_name][shift]['Downtime_count'] = idle_hours
            merged_idle_data[equipment_name][shift]['reasons'][downtime_reason] = idle_hours
            
        for result in breakdown_results: 
            equipment_name, shift, breakdown_hours, downtime_date, downtime_reason = result
            merged_breakdown_data[equipment_name][shift]['name'] = shift
            # merged_breakdown_daa[equipment_name][shift]['Total_Working_time'] = shift_duration[shift]["runtime"].seconds/60
            merged_breakdown_data[equipment_name][shift]['Breakdown_downtime'] += breakdown_hours
            merged_breakdown_data[equipment_name][shift]['Downtime_count'] = breakdown_hours
            merged_breakdown_data[equipment_name][shift]['reasons'][downtime_reason] = breakdown_hours

        for result in scheduled_results:
            equipment_name, shift, scheduled_hours, downtime_date, downtime_reason = result
            merged_scheduled_data[equipment_name][shift]['name'] = shift
            # merged_scheduled_data[equipment_name][shift]['Total_Working_time'] = shift_duration[shift]["runtime"].seconds/60
            merged_scheduled_data[equipment_name][shift]['Scheduled_downtime'] += scheduled_hours
            merged_scheduled_data[equipment_name][shift]['Downtime_count'] = scheduled_hours
            merged_scheduled_data[equipment_name][shift]['reasons'][downtime_reason] = scheduled_hours

        
        # Merge idle and breakdown data into a common structure
        merged_data = []
        equipment_names = set(merged_idle_data.keys()) | set(merged_breakdown_data.keys()) | set(merged_scheduled_data.keys())
        for equipment_name in equipment_names:
            equipment_entry = {'machine_name': equipment_name}
            shift_names = set(merged_idle_data.get(equipment_name, {}).keys()) | set(merged_breakdown_data.get(equipment_name, {}).keys()) | set(merged_scheduled_data.get(equipment_name, {}).keys())

            for shift in shift_names:
                idle_data = merged_idle_data[equipment_name][shift]
                scheduled_data = merged_scheduled_data[equipment_name][shift]
                breakdown_data = merged_breakdown_data[equipment_name][shift]
                shift_key = f"shift {shift}"
                total = shift_duration[shift]['runtime'].seconds/60
                equipment_entry[shift_key] = []
                shift_entry = {
                    'name': shift_key,
                    'total_working_time': round(float(total),2),
                    'running_time': round(float(round(float(total),2)- (round(float(idle_data['Idle_downtime']),2) + round(float(breakdown_data['Breakdown_downtime']),2) + round(float(scheduled_data['Scheduled_downtime']),2))),2),
                    'idle_downtime': round(float(idle_data['Idle_downtime']),2),
                    'breakdown_downtime': round(float(breakdown_data['Breakdown_downtime']),2),
                    'scheduled_downtime': round(float(scheduled_data['Scheduled_downtime']),2),
                    'idle_reasons': [{'reason': reason, 'count': count} for reason, count in idle_data['reasons'].items()],
                    'breakdown_reasons': [{'reason': reason, 'count': count} for reason, count in breakdown_data['reasons'].items()],
                    'scheduled_reasons': [{'reason': reason, 'count': count} for reason, count in scheduled_data['reasons'].items()],
                        
                }
                equipment_entry[shift_key].append(shift_entry)

            merged_data.append(equipment_entry)

        
        # Return the merged and transformed data
        return merged_data

        
    
        