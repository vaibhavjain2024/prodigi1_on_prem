from datetime import date, timedelta

import pytz

from app.modules.PSM.repositories.models.msil_batch import MSILBatch
from app.modules.PSM.repositories.models.msil_downtime import MSILDowntime
from app.modules.PSM.repositories.models.msil_downtime_reason import MSILDowntimeReasons
from app.modules.PSM.repositories.models.msil_equipment import MSILEquipment
from app.modules.PSM.repositories.models.msil_model import MSILModel
from app.modules.PSM.repositories.models.msil_part import MSILPart
from app.modules.PSM.repositories.models.msil_plan import MSILPlan, PlanStatusEnum
from app.modules.PSM.repositories.models.msil_production import MSILProduction
from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from app.modules.PSM.repositories.models.msil_shift import MSILShift
from app.modules.PSM.repositories.models.msil_shop_breaks import MSILShopBreaks
from .repository import Repository
from .models.msil_machine_telemetry import MSILMachineTelemetry
from sqlalchemy.orm import Session, aliased
import datetime
from .formulas import get_efficiency_by_shop_id,get_sph_by_shop_id
from sqlalchemy import and_, case, cast, Date, Time, func, or_

class MSILTelemetryRepository(Repository):
    """MSILTelemetryRepository to manage MSILTelemetry data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILMachineTelemetry

    def update_production_qty(self, production_id, material_code, quantity):
        with self.session:
            production = self.session.query(MSILProduction) \
                                     .filter(MSILProduction.id == production_id).first()
            self.session.query(MSILBatch) \
                        .filter(MSILBatch.production_id == production_id) \
                        .filter(MSILBatch.material_code == material_code) \
                        .filter(MSILBatch.end_time == None) \
                        .update({MSILBatch.prod_qty: MSILBatch.prod_qty + quantity})
            self.session.commit()

            batch = self.session.query(MSILBatch) \
                        .filter(MSILBatch.production_id == production_id) \
                        .filter(MSILBatch.material_code == material_code) \
                        .filter(MSILBatch.end_time == None) \
                        .first()
            
            self.session.query(MSILQualityPunching) \
                        .filter(MSILQualityPunching.batch_id == batch.id) \
                        .update({MSILQualityPunching.hold_qty: MSILQualityPunching.hold_qty + quantity})
            self.session.commit()

            plan = self.session.query(MSILPlan) \
                                    .filter(MSILPlan.production_date == production.date) \
                                    .filter(MSILPlan.equipment_id == production.equipment_id) \
                                    .filter(MSILPlan.material_code == material_code).first()
            if plan:
                plan.status = PlanStatusEnum.RUNNING
                self.session.merge(plan)
                self.session.commit()

    def get_runtime_by_shift(self, shop_id, shift_object_list):
        with self.session:
            # shifts = self.session.query(MSILShift) \
            #             .filter(MSILShift.shop_id == shop_id) \
            #             .all()
            shifts = shift_object_list
            breaks = self.session.query(MSILShopBreaks) \
                                 .filter(MSILShopBreaks.shop_id == shop_id) \
                                 .all()
            shift_obj = {}
            for shift in shifts:
                shift_start = shift.shift_start_timing
                shift_end = shift.shift_end_timing
                # shift_break_time = datetime.timedelta()
                # for shop_break in breaks:
                #     break_start = shop_break.start_time
                #     break_end = shop_break.end_time
                #     if break_end > shift_start and break_start < shift_end:
                #         shift_break_time +=  \
                #                 (datetime.datetime.combine(date.today(),min(break_end, shift_end)) - \
                #                 datetime.datetime.combine(date.today(),max(break_start,shift_start)))
                shift_obj[shift.shift_name] = {
                    "runtime" : (datetime.datetime.combine(date.today(),shift_end) 
                                 - datetime.datetime.combine(date.today(),shift_start)) 
                                    
                }
            return shift_obj
        
    def get_downtime_subquery( self,
                      shop_id, 
                      days,
                      timedelta_start,
                      shift_start_time,
                      shifts,
                      shift_object_list,
                      machine_list=None, 
                      model_list=None, 
                      part_list=None,
                      shift=None,
                      batch_st=None,
                      batch_et=None):
        
        with self.session:
            
            input_1_part = aliased(MSILPart)
            input_2_part = aliased(MSILPart)

            ist_tz = pytz.timezone('Asia/Kolkata')
            cur_datetime = datetime.datetime.now(ist_tz)
            cur_time = cur_datetime.time()
            current_date = datetime.date.today()
            prod_date = current_date
            if cur_time < shift_start_time:
                prod_date = prod_date - timedelta(days=1)

            current_shift = "NA"
            current_shift_start_time = None
            for label, start_time, end_time in shifts:
                if cur_time > start_time and cur_time < end_time:
                    current_shift = label
                    current_shift_start_time = start_time
                
            if current_shift == "NA":
                raise Exception("Current shift not found!")
            
            ## Get current runtime for edge case of ongoing shift report
            current_runtime = (cur_datetime - ist_tz.localize(datetime.datetime.combine(current_date,current_shift_start_time))).seconds/60 

            date_subquery = self.session.query(
                                    MSILEquipment.name.label("machine"),
                                    MSILEquipment.equipment_group.label("machine_group"),
                                    case(
                                    (MSILDowntime.end_time.is_(None),
                                    (func.extract('epoch', cur_datetime) - func.extract('epoch', func.timezone('-05:30', MSILDowntime.start_time))) / 60),
                                    else_=MSILDowntime.duration
                                    ).label("duration"),
                                    cast(MSILDowntime.start_time - timedelta_start, Date).label("prod_date"),
                                    MSILDowntime.shift.label("shift"),
                                    MSILDowntimeReasons.reason_type.label("reason_type")) \
                                .select_from(MSILDowntime) \
                                .filter(MSILDowntime.shop_id == shop_id) \
                                .join(MSILEquipment, MSILDowntime.equipment_id == MSILEquipment.id) \
                                .join(MSILDowntimeReasons, MSILDowntimeReasons.id == MSILDowntime.reason_id)

            
            if machine_list:
                date_subquery = date_subquery.filter(MSILEquipment.name.in_(machine_list)) 
            if batch_st and batch_et:
                date_subquery = date_subquery.filter(MSILDowntime.start_time >= batch_st)
                date_subquery = date_subquery.filter(MSILDowntime.start_time <= batch_et)

            if part_list or model_list:
                date_subquery = date_subquery.join(input_1_part, MSILDowntime.material_code == input_1_part.material_code) \
                                             .join(input_2_part, MSILDowntime.part_2_material_code == input_2_part.material_code, isouter=True)


                if part_list:
                    date_subquery = date_subquery.filter(or_(input_1_part.part_name.in_(part_list), input_2_part.part_name.in_(part_list)))
                
                if model_list:
                    date_subquery = date_subquery.join(MSILModel, MSILModel.id== input_1_part.model_id)
                    date_subquery = date_subquery.filter(MSILModel.model_name.in_(model_list))
            
            if shift:
                date_subquery = date_subquery.filter(MSILDowntime.shift.in_(shift))
            date_subquery = date_subquery.subquery()
            

            runtimes = self.get_runtime_by_shift(shop_id, shift_object_list)
            # return runtimes
            
            runtime_case_list = [
                        (date_subquery.c.shift == shift_name, runtimes[shift_name]["runtime"].seconds/60)
                        for shift_name in runtimes.keys()
                    ]
            ongoing_shift_edge_case = (and_(date_subquery.c.prod_date == prod_date, 
                                            date_subquery.c.shift == current_shift), 
                                            current_runtime)
            runtime_case_list.insert(0, ongoing_shift_edge_case)
            runtime_case = case(
                    *runtime_case_list
                    ,
                    else_=0
                    )
            downtime_prep_subquery = self.session.query(
                date_subquery.c.machine.label("machine"),
                date_subquery.c.machine_group.label("machine_group"),
                date_subquery.c.prod_date.label("prod_date"),
                date_subquery.c.shift.label("shift"),
                func.sum(case((date_subquery.c.reason_type == "scheduled", date_subquery.c.duration), else_=0)).label("scheduled_duration"),
                func.sum(case((date_subquery.c.reason_type == "idle", date_subquery.c.duration), else_=0)).label("idle_duration"),
                func.sum(case((date_subquery.c.reason_type == "breakdown", date_subquery.c.duration), else_=0)).label("breakdown_duration"),
                runtime_case.label("runtime")
                ) \
                    .filter(date_subquery.c.prod_date.in_(days)) \
                    .group_by(date_subquery.c.machine_group, 
                              date_subquery.c.machine,
                              date_subquery.c.prod_date,
                              date_subquery.c.shift) \
            
            return downtime_prep_subquery.subquery()


    def get_production_report(self, shop_id, 
                            start_date, 
                            end_date,
                            shift_list,
                            shift_object_list,
                            day_start,  
                            machine_list=None, 
                            model_list=None, 
                            part_list=None,
                            shift=None,
                            in_minutes = False,
                            batch_st=None,
                            batch_et=None):
        
        def date_range(start_date, end_date):
            
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += datetime.timedelta(days=1)
            return date_list
        days = date_range(start_date , end_date)
        print(days)
        with self.session:
            

            # shifts = self.session.query(MSILShift.shift_name,
            #                             MSILShift.shift_start_timing, 
            #                             MSILShift.shift_end_timing) \
            #                     .filter(MSILShift.shop_id==shop_id).all()
            shifts = shift_list

            # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
            # start = start_query.shift_start_timing
            start = day_start

            timedelta_start = datetime.timedelta(hours=start.hour, minutes=start.minute)

            time_column = cast(self.model_type.timestamp, Time)

            shift_case = case(
                *[
                    (time_column.between(start_time, end_time), label)
                    for label, start_time, end_time in shifts
                ]
                ,
                else_="NA"
                )
                        
            date_shift_subquery = \
                self.session.query(MSILEquipment.id.label('equipment_id'),
                                   MSILEquipment.name.label("machine"),
                                   MSILEquipment.equipment_group.label("machine_group"),
                                   self.model_type.quantity.label("quantity"),
                                   self.model_type.quantity.label("sph_quantity"),
                                   self.model_type.station_counter_type,
                                   cast(self.model_type.timestamp - timedelta_start, Date).label("prod_date"),
                                   shift_case.label("shift")) \
                            .select_from(self.model_type) \
                            .join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id) 
                
            if machine_list:
                date_shift_subquery = date_shift_subquery.filter(MSILEquipment.name.in_(machine_list)) 

            if batch_st and batch_et:
                date_shift_subquery = date_shift_subquery.filter(self.model_type.timestamp >= batch_st)
                date_shift_subquery = date_shift_subquery.filter(self.model_type.timestamp <= batch_et)
                

            if part_list or model_list:
                date_shift_subquery = date_shift_subquery.join(MSILPart, self.model_type.material_code == MSILPart.material_code)

                if part_list:
                    date_shift_subquery = date_shift_subquery.filter(MSILPart.part_name.in_(part_list))
                
                if model_list:
                    date_shift_subquery = date_shift_subquery.join(MSILModel, MSILModel.id== MSILPart.model_id)
                    date_shift_subquery = date_shift_subquery.filter(MSILModel.model_name.in_(model_list))
            
            date_shift_subquery = date_shift_subquery.subquery()     
            plan_subquery = self.session.query(MSILPlan.equipment_id.label("plan_eqp_id"),(func.sum(MSILPlan.planned_quantity)).label("target")) \
                            .filter(MSILPlan.production_date.in_(days)) \
                            .group_by(MSILPlan.equipment_id) \
                            .subquery()
                    
            prod_qty_report = self.session.query(
                    date_shift_subquery.c.equipment_id,
                    date_shift_subquery.c.machine.label("machine"),
                    date_shift_subquery.c.machine_group.label("machine_group"),
                    func.sum(date_shift_subquery.c.quantity).label("total_quantity"),
                    func.sum(date_shift_subquery.c.sph_quantity).label("total_sph_quantity"),
                    date_shift_subquery.c.prod_date.label("prod_date"),
                    date_shift_subquery.c.shift.label("shift"),
                    date_shift_subquery.c.station_counter_type,
                ) \
                .filter(date_shift_subquery.c.prod_date.in_(days))
                                

            if shift:
                prod_qty_report = prod_qty_report.filter(date_shift_subquery.c.shift.in_(shift))


            downtime = self.get_downtime_subquery(shop_id,
                                                  days,
                                                  timedelta_start,
                                                  start,
                                                  shifts,
                                                  shift_object_list,
                                                  machine_list,
                                                  model_list,
                                                  part_list,
                                                  shift,
                                                  batch_st=batch_st,
                                                  batch_et=batch_et)
            # return downtime

            prod_qty = prod_qty_report \
                    .group_by(date_shift_subquery.c.machine_group, 
                              date_shift_subquery.c.machine,
                              date_shift_subquery.c.prod_date,
                              date_shift_subquery.c.shift,
                              date_shift_subquery.c.station_counter_type,
                              date_shift_subquery.c.equipment_id
                              ) \
                    .subquery()
            
            prod_qty = self.session.query(
                                prod_qty.c.equipment_id,
                                prod_qty.c.machine,
                                prod_qty.c.machine_group,
                                prod_qty.c.prod_date,
                                prod_qty.c.shift,
                                func.sum(prod_qty.c.total_quantity).label('quantity'),
                                func.max(prod_qty.c.total_sph_quantity).label("sph_quantity")
                            ).group_by(prod_qty.c.machine_group, 
                              prod_qty.c.equipment_id,
                              prod_qty.c.machine,
                              prod_qty.c.prod_date,
                              prod_qty.c.shift
                              ).subquery()

            return self.session.query(prod_qty.c.machine,
                                prod_qty.c.machine_group,
                                prod_qty.c.prod_date,
                                prod_qty.c.shift,
                                prod_qty.c.quantity,
                                downtime.c.runtime, 
                                downtime.c.idle_duration, 
                                downtime.c.breakdown_duration,
                                downtime.c.scheduled_duration,
                                # (prod_qty.c.quantity*60 / (downtime.c.runtime - (downtime.c.idle_duration + downtime.c.breakdown_duration))).label("SPH"),
                                get_sph_by_shop_id(shop_id,prod_qty.c.sph_quantity,downtime.c.runtime,downtime.c.idle_duration,downtime.c.breakdown_duration,downtime.c.scheduled_duration).label("SPH"),
                                # ((downtime.c.runtime - downtime.c.breakdown_duration) / (downtime.c.runtime - downtime.c.idle_duration) * 100).label("efficiency")
                                get_efficiency_by_shop_id(shop_id,downtime.c.breakdown_duration,downtime.c.idle_duration,downtime.c.runtime,downtime.c.scheduled_duration,in_minutes,actual_prod=prod_qty.c.quantity,planned_prod=plan_subquery.c.target).label("efficiency"),
                                prod_qty.c.sph_quantity
                            ) \
                            .join(plan_subquery,plan_subquery.c.plan_eqp_id == prod_qty.c.equipment_id,isouter=True)\
                            .join(downtime, and_(
                                prod_qty.c.machine == downtime.c.machine,
                                prod_qty.c.machine_group == downtime.c.machine_group,
                                prod_qty.c.prod_date == downtime.c.prod_date,
                                prod_qty.c.shift == downtime.c.shift
                            )) \
                            .order_by(prod_qty.c.prod_date, prod_qty.c.machine_group) \
                            .all()
        
    def get_part_wise_metrics(self, shop_id, shift_name_start_end_list, first_shift_time,start_date, end_date):

        def date_range(start_date, end_date):    
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += datetime.timedelta(days=1)
            return date_list
        days = date_range(start_date , end_date)

        with self.session:
            shifts = shift_name_start_end_list
            # shifts = self.session.query(MSILShift.shift_name,
            #                 MSILShift.shift_start_timing, 
            #                 MSILShift.shift_end_timing) \
            #         .filter(MSILShift.shop_id==shop_id).all()
            start = first_shift_time
            # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
            # start = start_query.shift_start_timing

            timedelta_start = datetime.timedelta(hours=start.hour, minutes=start.minute)

            time_column = cast(self.model_type.timestamp, Time)

            shift_case = case(
                *[
                    (time_column.between(start_time, end_time), label)
                    for label, start_time, end_time in shifts
                ]
                ,
                else_="NA"
                )
            
            date_shift_subquery = \
                self.session.query(MSILEquipment.name.label("machine"),
                                   MSILEquipment.equipment_group.label("machine_group"),
                                   self.model_type.quantity.label("quantity"),
                                   MSILPart.part_name.label("part_name"),
                                   cast(self.model_type.timestamp - timedelta_start, Date).label("prod_date"),
                                   func.extract('hour', self.model_type.timestamp).label("hour"),
                                   shift_case.label("shift")) \
                            .select_from(self.model_type) \
                            .join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id)  \
                            .join(MSILPart, self.model_type.material_code == MSILPart.material_code) \
                            .subquery()
            
            return self.session.query(
                date_shift_subquery.c.prod_date,
                date_shift_subquery.c.machine_group,
                date_shift_subquery.c.machine,
                date_shift_subquery.c.part_name,
                date_shift_subquery.c.shift,
                date_shift_subquery.c.hour,
                func.sum(date_shift_subquery.c.quantity)
            ) \
                .filter(date_shift_subquery.c.prod_date.in_(days)) \
                .group_by(
                    date_shift_subquery.c.prod_date,
                    date_shift_subquery.c.machine_group,
                    date_shift_subquery.c.machine,
                    date_shift_subquery.c.part_name,
                    date_shift_subquery.c.shift,
                    date_shift_subquery.c.hour
                ) \
                .all()
            

            

            


