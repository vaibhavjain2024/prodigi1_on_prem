from ..repositories.msil_equipment_repository import MSILEquipmentRepository
from ..repositories.models.msil_equipment import MSILEquipment
from ..repositories.msil_shift_repository import MSILShiftRepository
from .service import Service
import datetime
import pytz
ist_tz = pytz.timezone('Asia/Kolkata')
from modules.PSM.services.shift_util import get_shift,SHIFT_MAPPING_WITH_TIME,get_shift_with_start_end
class MSILEquipmentService(Service):
    def __init__(self, repository : MSILEquipmentRepository, shift_repo: MSILShiftRepository):
        super().__init__(repository, self.transform_model_to_dict, 
                         self.transform_dict_to_model)
        self.repository = repository
        self.shift_repository = shift_repo
    
    def get_machines_by_shop(self, shop_id):
        machines = self.repository.get_machines_by_shop(shop_id)
        return self._Service__transform_model_list(machines)

    def get_all_shops(self):
        shops = self.repository.get_all_shops()
        shop_list = []
        for shop in shops:
            shop_list.append(shop[0])
        return shop_list
    
    def update_SPM(self, equipment_id, SPM, shop_id):
        self.repository.update_SPM(equipment_id, SPM, shop_id)    
    
    def get_machine_name_cache(self):
        machines = self.repository.get_all()
        machine_name_cache = {}
        for machine in machines:
            if machine_name_cache.get(str(machine.shop_id),None) == None:
                machine_name_cache[str(machine.shop_id)] = {}
            machine_name_cache[str(machine.shop_id)][machine.name] = machine.id
        return machine_name_cache

    
    def transform_model_to_dict(self, model : MSILEquipment):
        return {
            "id" : model.id,
            "machine_group" : model.equipment_group,
            "machine" : model.name,
            "make" : model.make,
            "capacity" : model.capacity,
            "description" : model.description,
            "capacity_uom" : model.capacity_uom,
            "purchase_year" : model.purchase_year,
            "shop_id" : model.shop_id,
            "line_id" : model.line_id
        }
    
    def transform_dict_to_model(self, dict):
        pass

    def machine_shop_view(self, sorted_object):
        # print("sorted_object :" , sorted_object)
        model: MSILEquipment = sorted_object[0]
        target = sorted_object[1]
        actual = sorted_object[2]
        planned_stop = sorted_object[3]
        downtime = sorted_object[4]
        target_percent = sorted_object[5]
        efficiency = sorted_object[6]
        critical = sorted_object[7]
        sph = sorted_object[8]
        sph_max = sorted_object[9] 
        sph_actual = sorted_object[10]
        actual_max = sorted_object[11]
        return {
            "machine_group":model.equipment_group,
            "machine_name":model.name,
            "target":round(float(target),2),
            "target_percent":round(float(target_percent),2),
            "actual":actual,
            "status": model.status,
            "sph": round(float(sph),2),
            "efficiency":round(float(efficiency),2),
            "downtime":round(float(downtime),2),
            "planned_stop":round(float(planned_stop),2),
            "critical":critical,
            "sph_max" : sph_max,
            "sph_actual" : sph_actual,
            "actual_max" : actual_max
        }
    
    def machine_shop_view_new(self, sorted_object,runtime,work_hours,view="CURRENT"):
        # print("sorted_object :" , sorted_object)
        model: MSILEquipment = sorted_object[0]
        target = sorted_object[1] if view == "CURRENT" else sorted_object[1] / 3
        actual = sorted_object[2]
        planned_stop = sorted_object[3]
        downtime = sorted_object[4]
        active_breakdown = sorted_object[5]
        active_idle = sorted_object[6]
        active_scheduled = sorted_object[7]
        total_stroke = sorted_object[8] if 'Blanking' not in model.equipment_group else actual
        target_percent = sorted_object[9] if sorted_object[9] != 0 else 100
        efficiency = sorted_object[10]
        sph = sorted_object[11]
        current_target = target*runtime/work_hours if (target*runtime/work_hours) < target else target
        pph = float(actual)/work_hours
        capacity_utilization_rate = float(actual)/target if target > 0 else 100
        return {
            "machine_group":model.equipment_group,
            "machine_name":model.name,
            "target":round(float(target),2),
            "target_percent":round(float(target_percent),2),
            "actual":actual,
            "status": model.status,
            "total_stroke": round(float(total_stroke),2),
            "sph": round(float(sph),2),
            "efficiency":round(float(efficiency),2),
            "total_downtime":round(float(downtime),2),
            "planned_stop":round(float(planned_stop),2),
            "active_breakdown":round(float(active_breakdown),2),
            "active_idle":round(float(active_idle),2),
            "active_scheduled":round(float(active_scheduled),2),
            "current_target":round(float(current_target),2),
            "pph": round(float(pph),2),
            "capacity_utilization_rate": round(float(capacity_utilization_rate),2)
        }
    
    def get_shop_view(self, shop_id, machine_name=None, machine_group=None, view="DAY",is_mailer = False,batch_st=None,batch_et=None,material_code=None):
        start_time = self.shift_repository.day_start_time(shop_id=shop_id)
        end_time = self.shift_repository.day_end_time(shop_id=shop_id)
        if is_mailer:
            cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None) - datetime.timedelta(hours=1)
            shift,start_time,end_time = get_shift_with_start_end(cur_datetime.time())
            view = "CURRENT"
            if batch_st is not None and batch_et is not None:
                start_time = batch_st
                end_time = batch_et
            print(start_time,end_time)
        if view not in ("DAY","CURRENT"):
            raise Exception("Invalid View")
        else:
            result = self.repository.get_shop_view(shop_id=shop_id,name=machine_name,group=machine_group,view=view,start_time=start_time,end_time=end_time,material_code=material_code)
        machine_list = []
        running = 0
        idle = 0
        breakdown = 0
        scheduled=0
        critical = 0
        high = 0
        medium = 0
        low = 0
        for shop_item in result:
            # Identify actual number of elements (uncomment and run before using the function)
            # print(len(shop_item))

            # Adjust unpacking based on actual number of elements
            actual_length = len(shop_item)  # Replace with the actual number obtained above
            equipment_object, target, actual, planned_stop, downtime, target_percent, efficiency, critical, sph, sph_max, sph_actual, *remaining_values = shop_item


            # print(f"""
            # Equipment: {equipment_object}  # Replace with actual equipment identifier if needed
            # Target: {target}
            # Actual: {actual}
            # Planned Stop: {planned_stop}
            # Downtime: {downtime}
            # Target Percent: {target_percent}
            # Efficiency: {efficiency:.2f}  # Format efficiency with 2 decimal places
            # Critical: {critical}
            # SPH: {sph}
            # SPH Max: {sph_max}
            # SPH Actual: {sph_actual}
            # """)

            # if remaining_values:
            #     print(f"** Additional Values (might require further investigation): {remaining_values}")

            machine_list.append(self.machine_shop_view(shop_item))
        
        for item in machine_list:
            if item["status"] == "RUNNING":
                running=running+1
            elif item["status"] == "IDLE":
                idle=idle+1
            elif item["status"] == "BREAKDOWN":
                breakdown=breakdown+1
            elif item["status"] == "SCHEDULED":
                scheduled=scheduled+1

            if item["critical"] ==1:
                critical = critical+1
        
            if item["target_percent"] >= 95:
                high = high+1
            elif item["target_percent"] >= 90:
                medium = medium+1
            elif item["target"] == 0:
                high = high+1
            else:
                low = low+1

        status={
            "RUNNING" : running,
            "BREAKDOWN" : breakdown,
            "IDLE" : idle,
            "SCHEDULED": scheduled,
            "CRITICAL" : critical
        }

        achieved = {
            "high" : high,
            "medium" : medium,
            "low" : low
        }

        output = {
            "machine_list":machine_list,
            "status":status,
            "achieved":achieved
        }

        return output
    
    def shop_view_report(self, csvwriter, shop_id, machine_name=None, machine_group=None, view="DAY"):
        start_time = self.shift_repository.day_start_time(shop_id=shop_id)
        end_time = self.shift_repository.day_end_time(shop_id=shop_id)
        if view not in ("DAY","CURRENT"):
            raise Exception("Invalid View")
        else:
            result = self.repository.get_shop_view(shop_id=shop_id,name=machine_name,group=machine_group,view=view,start_time=start_time,end_time=end_time)
        
        
        # fields = [ 'Machine Group', 'Machine Name', 'Target', 'Target Percent', 'Actual', 'Status', 'SPH', 'Efficiency', 'Downtime', 'Planned Stop', 'Critical' ]
        # downtime_dict = []
        # rows = []
        # csvwriter.writerow(fields)

        machine_list = []

        for shop_item in result:
            machine_list.append(self.machine_shop_view(shop_item))
        
        return machine_list
        
        # for item in machine_list:
        #     fields = list(item.values())
        #     csvwriter.writerow(fields)
        #     rows.append(fields)
        # return rows
    
    def shop_view_graph(self, shop_id, machine_name, view):
        start_time = self.shift_repository.day_start_time(shop_id=shop_id)
        end_time = self.shift_repository.day_end_time(shop_id=shop_id)
        actual_line = self.repository.actual_graph(shop_id=shop_id,name=machine_name,start_time=start_time,end_time=end_time)
        if view not in ("DAY","CURRENT"):
            raise Exception("Invalid View")
        else:
            target_line = self.repository.target_graph(shop_id=shop_id,name=machine_name,view=view,start_time=start_time,end_time=end_time)

        output = {'target_line':target_line,'actual_line':actual_line}
        return output
    
    def get_machine_view(self, shop_id, machine_name=None, machine_group=None, view="CURRENT"):

        start_time = self.shift_repository.day_start_time(shop_id=shop_id)
        end_time = self.shift_repository.day_end_time(shop_id=shop_id)
        if view == "CURRENT_SHIFT":
            ist_tz = pytz.timezone('Asia/Kolkata')
            current_time = datetime.datetime.now(ist_tz).time().replace(microsecond=0)
            shift_data = self.shift_repository.get_shift_start_and_end_time(shop_id,current_time)
            start_time = shift_data['shift_start_timing']
            end_time = shift_data['shift_end_timing']
            # print("shift_data",shift_data)
        if view not in ("CURRENT_SHIFT","CURRENT"):
            raise Exception("Invalid View")
        else:
            result,runtime,work_hours = self.repository.get_machine_view(shop_id=shop_id,name=machine_name,group=machine_group,view=view,start_time=start_time,end_time=end_time)
        machine_list = []
        running = 0
        idle = 0
        breakdown = 0
        scheduled=0
        # critical = 0
        # high = 0
        # medium = 0
        # low = 0
        for shop_item in result:
            # Identify actual number of elements (uncomment and run before using the function)
            # print(len(shop_item))

            # Adjust unpacking based on actual number of elements
            actual_length = len(shop_item)  # Replace with the actual number obtained above
            equipment_object, target, actual, planned_stop, downtime, active_breakdown, active_idle,active_scheduled, total_stroke,target_percent, efficiency, sph_max, sph_actual, *remaining_values = shop_item


            # print(f"""
            # Equipment: {equipment_object}  # Replace with actual equipment identifier if needed
            # Day_Target: {target}
            # Current_Target : {target*runtime/work_hours}
            # Actual: {actual}
            # Planned Stop: {planned_stop}
            # Downtime: {downtime}
            # active_breakdown: {active_breakdown}
            # active_idle: {active_idle},
            # active_scheduled: {active_scheduled}
            # Target Percent: {target_percent}
            # Efficiency: {efficiency:.2f}  # Format efficiency with 2 decimal places
            # total_stroke: {total_stroke}
            # """)

            # if remaining_values:
            #     print(f"** Additional Values (might require further investigation): {remaining_values}")

            machine_list.append(self.machine_shop_view_new(shop_item,runtime,work_hours,view))
        
        for item in machine_list:
            if item["status"] == "RUNNING":
                running=running+1
            elif item["status"] == "IDLE":
                idle=idle+1
            elif item["status"] == "BREAKDOWN":
                breakdown=breakdown+1
            elif item["status"] == "SCHEDULED":
                scheduled=scheduled+1

        status={
            "RUNNING" : running,
            "BREAKDOWN" : breakdown,
            "IDLE" : idle,
            "SCHEDULED": scheduled
        }


        output = {
            "machine_list":machine_list,
            "status":status
        }

        return output
    
    def machine_view_graph(self, shop_id, view="CURRENT", machine_name=None):
        start_time = self.shift_repository.day_start_time(shop_id=shop_id)
        end_time = self.shift_repository.day_end_time(shop_id=shop_id)
        if view == "CURRENT_SHIFT":
            ist_tz = pytz.timezone('Asia/Kolkata')
            current_time = datetime.datetime.now(ist_tz).time().replace(microsecond=0)
            shift_data = self.shift_repository.get_shift_start_and_end_time(shop_id,current_time)
            start_time = shift_data['shift_start_timing']
            end_time = shift_data['shift_end_timing']
            print("shift_data",shift_data)
            actual_line = self.repository.actual_graph_new(shop_id=shop_id,name=machine_name,start_time=start_time,end_time=end_time)
        if view not in ("DAY","CURRENT"):
            raise Exception("Invalid View")
        else:
            target_line = self.repository.target_graph_new(shop_id=shop_id,name=machine_name,view=view,start_time=start_time,end_time=end_time)
            result = self.repository.get_machine_actual_plan_stroke_breakdown_and_die_change_data(shop_id=shop_id,machine_id=None,start_time=start_time,end_time=end_time,) #view=view)
        output = {'target_line':target_line}#,'actual_line':actual_line}
        return output