import datetime
# from pandas import DataFrame

import pytz
from app.modules.PSM.repositories.models.msil_machine_telemetry import MSILMachineTelemetry
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from ..repositories.msil_telemetry_repository import MSILTelemetryRepository
from .service import Service

ist_tz = pytz.timezone('Asia/Kolkata')

class MSILTelemetryService(Service):
    def __init__(self, repository : MSILTelemetryRepository, shift_repo : MSILShiftRepository):
        self.repository = repository
        self.shift_repository = shift_repo

    def add_telemetry(self, production_id, equipment_id, material_code, quantity, timestamp,station_counter_type):
        telemetry = MSILMachineTelemetry()
        telemetry.equipment_id = equipment_id
        telemetry.material_code = material_code
        telemetry.quantity = quantity
        telemetry.station_counter_type = station_counter_type
        dt_object = datetime.datetime.fromtimestamp(timestamp, ist_tz).replace(tzinfo=None)
        telemetry.timestamp = dt_object
        self.repository.add(telemetry)
        self.repository.update_production_qty(production_id, material_code, quantity)

    def get_efficiency(self, machine_efficiency):
        if 0 < machine_efficiency < 100:
            return machine_efficiency
        elif machine_efficiency > 100:
            return 100
        else:
            return 0

    def get_production_report(self, shop_id, 
                            start_date, 
                            end_date,  
                            machine_list=None, 
                            model_list=None, 
                            part_list=None,
                            shift=None,
                            in_minutes = False,
                            batch_st = None,
                            batch_et = None):
        print(f"shop_id ({type(shop_id).__name__}): {shop_id}")
        print(f"start_date ({type(start_date).__name__}): {start_date}")
        print(f"end_date ({type(end_date).__name__}): {end_date}")
        print(f"machine_list ({type(machine_list).__name__}): {machine_list}")
        print(f"model_list ({type(model_list).__name__}): {model_list}")
        print(f"part_list ({type(part_list).__name__}): {part_list}")
        print(f"shift ({type(shift).__name__}): {shift}")
        print(f"in_minutes ({type(in_minutes).__name__}): {in_minutes}")
        print(f"batch_st ({type(batch_st).__name__}): {batch_st}")
        print(f"batch_et ({type(batch_et).__name__}): {batch_et}")
        day_start = self.shift_repository.day_start_time(shop_id=shop_id)
        shift_list = self.shift_repository.shift_name_start_end_list(shop_id=shop_id)
        shift_object_list = self.shift_repository.shift_object_list(shop_id=shop_id)

        production_data = self.repository.get_production_report(shop_id, 
                            start_date, 
                            end_date,
                            shift_list,
                            shift_object_list,
                            day_start,  
                            machine_list, 
                            model_list, 
                            part_list,
                            shift,
                            in_minutes,
                            batch_st=batch_st,
                            batch_et=batch_et)
        # return production_data
        
        production_report = {}
        
        for datapoint in production_data:
            machine_group = datapoint.machine_group
            machine = datapoint.machine
            prod_date = str(datapoint.prod_date)
            data_shift = datapoint.shift
            prod_quantity = datapoint.quantity
            runtime = float(datapoint.runtime)
            idle_duration = float(datapoint.idle_duration)
            breakdown_duration = float(datapoint.breakdown_duration)
            SPH = datapoint.SPH
            efficiency = datapoint.efficiency
            sph_quantity = datapoint.sph_quantity
            scheduled_duration =  datapoint.scheduled_duration
            print("datapoint.machine_group",datapoint.machine_group)
            print("datapoint.machine",datapoint.machine)
            print("datapoint.runtime",datapoint.runtime)
            print("datapoint.idle_duration",datapoint.idle_duration)
            print("datapoint.breakdown_duration",datapoint.breakdown_duration)
            print("datapoint.efficiency",datapoint.efficiency)
            print("datapoint.scheduled_duration",datapoint.scheduled_duration)
            if production_report.get(prod_date, None) == None:
                production_report[prod_date] = {}
            
            if production_report[prod_date].get(machine_group, None) == None:
                production_report[prod_date][machine_group] = {}

            if production_report[prod_date][machine_group].get(machine, None) == None:
                production_report[prod_date][machine_group][machine] = {}

            cal_efficiency = self.get_efficiency(efficiency)

            production_report[prod_date][machine_group][machine][data_shift] = {
                "prod_qty": int(prod_quantity),
                "runtime": runtime,
                "idle_duration": idle_duration,
                "breakdown_duration": breakdown_duration,
                "scheduled_duration" : scheduled_duration,
                "SPH": SPH if SPH > 0 else 0,
                "efficiency": cal_efficiency,
                "sph_qunatity": sph_quantity
            }

        production_metrics = {}
        machine_wise_metrics = {}
        for prod_date_key in production_report.keys():
            production_metrics[prod_date_key] = {}
            machine_wise_metrics[prod_date_key] = {}
            machine_group_data = production_report[prod_date_key]
            for machine_group_key in machine_group_data.keys():
                production_metrics[prod_date_key][machine_group_key] = {}
                production_metrics[prod_date_key][machine_group_key]["prod_qty"] = 0
                production_metrics[prod_date_key][machine_group_key]["idle_duration"] = 0
                production_metrics[prod_date_key][machine_group_key]["breakdown_duration"] = 0
                production_metrics[prod_date_key][machine_group_key]["runtime"] = 0

                machine_wise_metrics[prod_date_key][machine_group_key] = {}

                machine_data = machine_group_data[machine_group_key]
                for machine_key in machine_data.keys():
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key] = {}
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["prod_qty"] = 0
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["idle_duration"] = 0
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["breakdown_duration"] = 0
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["runtime"] = 0
                    shift_data = machine_data[machine_key]
                    for shift_key in shift_data.keys():
                        metrics = shift_data[shift_key]
                        production_metrics[prod_date_key][machine_group_key]["prod_qty"] += metrics["prod_qty"]
                        production_metrics[prod_date_key][machine_group_key]["idle_duration"] += metrics["idle_duration"]
                        production_metrics[prod_date_key][machine_group_key]["breakdown_duration"] += metrics["breakdown_duration"]
                        production_metrics[prod_date_key][machine_group_key]["runtime"] += metrics["runtime"]
                        machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["prod_qty"] += metrics["prod_qty"]
                        machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["idle_duration"] += metrics["idle_duration"]
                        machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["breakdown_duration"] += metrics["breakdown_duration"]
                        machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["runtime"] += metrics["runtime"]

                    machine_sph = 60 * (
                                machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["prod_qty"] / (
                                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["runtime"] - (
                                        machine_wise_metrics[prod_date_key][machine_group_key][machine_key][
                                            "breakdown_duration"] +
                                        machine_wise_metrics[prod_date_key][machine_group_key][machine_key][
                                            "idle_duration"])))
                    machine_efficiency = 100 * (
                                machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["runtime"] -
                                machine_wise_metrics[prod_date_key][machine_group_key][machine_key][
                                    "breakdown_duration"]) / (machine_wise_metrics[prod_date_key][machine_group_key][
                                                                  machine_key]["runtime"] -
                                                              machine_wise_metrics[prod_date_key][machine_group_key][
                                                                  machine_key]["idle_duration"])
                    if in_minutes:
                        machine_efficiency = 100 * (machine_wise_metrics[prod_date_key][machine_group_key][machine_key]["runtime"]) / (machine_wise_metrics[prod_date_key][machine_group_key][
                                                                  machine_key]["runtime"] +
                                                              machine_wise_metrics[prod_date_key][machine_group_key][
                                                                  machine_key]["idle_duration"] + machine_wise_metrics[prod_date_key][machine_group_key][machine_key][
                                    "breakdown_duration"])
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key][
                        "SPH"] = machine_sph if machine_sph > 0 else 0
                    machine_wise_metrics[prod_date_key][machine_group_key][machine_key][
                        "efficiency"] = self.get_efficiency(machine_efficiency)

                prod_metrics_sph = 60 * (production_metrics[prod_date_key][machine_group_key]["prod_qty"] / (
                            production_metrics[prod_date_key][machine_group_key]["runtime"] - (
                                production_metrics[prod_date_key][machine_group_key]["breakdown_duration"] +
                                production_metrics[prod_date_key][machine_group_key]["idle_duration"])))
                prod_metrics_effieiency = 100 * (production_metrics[prod_date_key][machine_group_key]["runtime"] -
                                                 production_metrics[prod_date_key][machine_group_key][
                                                     "breakdown_duration"]) / (
                                                      production_metrics[prod_date_key][machine_group_key]["runtime"] -
                                                      production_metrics[prod_date_key][machine_group_key][
                                                          "idle_duration"])
                if in_minutes:
                    prod_metrics_effieiency = 100 * (production_metrics[prod_date_key][machine_group_key]["runtime"]) / (
                                                      production_metrics[prod_date_key][machine_group_key]["runtime"] +
                                                      production_metrics[prod_date_key][machine_group_key][
                                                          "idle_duration"]+
                                                 production_metrics[prod_date_key][machine_group_key][
                                                     "breakdown_duration"])

                production_metrics[prod_date_key][machine_group_key][
                    "SPH"] = prod_metrics_sph if prod_metrics_sph > 0 else 0
                production_metrics[prod_date_key][machine_group_key]["efficiency"] = self.get_efficiency(
                    prod_metrics_effieiency)

        return production_metrics, production_report, machine_wise_metrics
        
    def get_production_report_excel(self, shop_id, 
                            start_date, 
                            end_date,  
                            writer=None,
                            machine_list=None, 
                            model_list=None, 
                            part_list=None,
                            shift=None):
        groupwise_data, machinewise_data, machinewise_metrics = self.get_production_report(shop_id=shop_id,start_date=start_date,
                                                                      end_date=end_date,
                                                                      machine_list=machine_list,
                                                                      model_list=model_list,
                                                                      part_list=part_list,
                                                                      shift=shift)
        groupwise_formatted = []
        machinewise_formatted = []
        metrics_formatted=[]

        # groupsheet = workbook.add_worksheet('Groupwise Report')
        # machinesheet = workbook.add_worksheet('Machinewise Report')

        for date in groupwise_data.keys():
            for group, group_values in groupwise_data[date].items():
                groupwise_formatted.append({
                    "Date":date,
                    "Machine Group":group,
                    "Production Quantity": group_values['prod_qty'],
                    "Runtime":group_values['runtime'],
                    "SPH": group_values['SPH'],
                    "Efficiency":group_values['efficiency']
                })

        for date in machinewise_data.keys():
            for group in machinewise_data[date].keys():
                for machine in machinewise_data[date][group].keys():
                    for shift, shift_data in machinewise_data[date][group][machine].items():
                        machinewise_formatted.append({
                            "Date":date,
                            "Machine Group":group,
                            "Machine":machine,
                            "Shift":shift,
                            "Production Quantity": shift_data['prod_qty'],
                            "Runtime":shift_data['runtime'],
                            "SPH": shift_data['SPH'],
                            "Efficiency":shift_data['efficiency']
                        })
        
        for date in machinewise_metrics.keys():
            for group in machinewise_metrics[date].keys():
                for machine, machine_items in machinewise_metrics[date][group].items():
                    metrics_formatted.append({
                        "Date":date,
                        "Machine Group":group,
                        "Machine":machine,
                        "Production Quantity": machine_items['prod_qty'],
                        "Runtime":machine_items['runtime'],
                        "SPH": machine_items['SPH'],
                        "Efficiency":machine_items['efficiency']
                    })
        
        # if writer:
        #     df_group = DataFrame(groupwise_formatted)
        #     df_machine = DataFrame(machinewise_formatted)
        #     df_metrics = DataFrame(machinewise_formatted)
            
        #     df_group.to_excel(writer,sheet_name='Groupwise Report',index=False)
        #     df_machine.to_excel(writer,sheet_name='Machinewise Report',index=False)
        #     df_metrics.to_excel(writer,sheet_name='Machinewise Metrics',index=False)
        #     writer.save()

        return {'Machinewise':machinewise_formatted,'Groupwise':groupwise_formatted, 'Machinewise Metrics':metrics_formatted}
