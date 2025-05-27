from .repository import Repository
from .models.msil_equipment import MSILEquipment
from .models.msil_downtime import MSILDowntime
from .models.msil_downtime_reason import MSILDowntimeReasons
from .models.msil_machine_telemetry import MSILMachineTelemetry
from .models.msil_plan import MSILPlan
from .models.msil_shop_breaks import MSILShopBreaks
from .models.msil_shift import MSILShift
from sqlalchemy.orm import Session
from sqlalchemy import extract
import datetime
from sqlalchemy import (
    and_,
    desc,
    func,
    case,
    column,
    cast,
    Date,
    Numeric,
    text,
    or_,
    not_
)
import pytz
from ..services.shift_util import get_day_start, get_day_end
from .formulas import get_efficiency_by_shop_id, get_sph_by_shop_id


class MSILEquipmentRepository(Repository):
    """
    MSILMachineRepository to manage MSILMachine data table.
    """

    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILEquipment

    def get_all_shops(self):
        with self.session:
            return self.session.query(MSILEquipment.shop_id) \
                               .distinct() \
                               .all()

    def get_machines_by_shop(self, shop_id):
        with self.session:
            return self.session.query(self.model_type) \
                               .filter(self.model_type.shop_id == shop_id,
                                       self.model_type.is_deleted == False) \
                               .all()

    def update_SPM(self, equipment_id, SPM, shop_id):
        with self.session:
            equipment = self.filter_by(id=equipment_id,
                                       shop_id=shop_id)
            equipment.SPM = SPM
            self.session.merge(equipment)
            self.commit()

    def update_status(self, equipment_id, reason, shop_id):
        print(f"update status of equipment id {equipment_id} to {reason}")
        with self.session:
            equipment = self.filter_by(id=equipment_id, shop_id=shop_id)
            equipment.status = reason.upper()
            self.session.merge(equipment)
            self.commit()

    def get_shop_view(self, shop_id, start_time, end_time, name=None, group=None, view="DAY", material_code=None):

        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        # cur_datetime = ist_tz.localize(datetime.datetime.strptime('2023-10-28 01:00:00','%Y-%m-%d %H:%M:%S')).replace(tzinfo=None)
        cur_time = cur_datetime.time()
        cur_date = cur_datetime.date()

        # if view=="DAY":
        #     runtime = (cur_datetime - shift_start).total_seconds()/60

        with self.session:

            # get the first shift
            # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()

            # calculate the start time of the first shift
            start = start_time

            # if current time is less than start time of the shift, production date is the previous date
            if cur_time < start:
                start_date = cur_date - datetime.timedelta(days=1)
                end_date = cur_date
            else:
                start_date = cur_date
                end_date = cur_date + datetime.timedelta(days=1)

            # start datetime of the production date
            start_time = ist_tz.localize(datetime.datetime.combine(
                start_date, start)).replace(tzinfo=None)

            # get the last shift
            # end_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name.desc()).first()

            # day end is the end of last shift
            end = end_time

            # if the end of last shift is less than the start of first shift, the last shift ends on the next day
            if end < start:
                end_time = ist_tz.localize(datetime.datetime.combine(end_date, end)).replace(
                    minute=30, second=0, microsecond=0, tzinfo=None)
            else:
                end_time = ist_tz.localize(datetime.datetime.combine(cur_date, end)).replace(
                    minute=30, second=0, microsecond=0, tzinfo=None)

            # working hours is the difference between end time of last shift and start time of first shift
            work_hours = (end_time-start_time).total_seconds()/3600

            # return start_time, end_time, cur_datetime, work_hours, cur_time
            greater_than_start = cur_time > start
            break_duration = 0

            if greater_than_start:
                breaks = self.session.query(MSILShopBreaks).filter(
                    MSILShopBreaks.shop_id == shop_id, MSILShopBreaks.start_time < cur_time, MSILShopBreaks.start_time > start)
                for item in breaks:
                    if item.end_time > cur_time:
                        break_duration += (cur_datetime - ist_tz.localize(datetime.datetime.combine(
                            cur_date, item.start_time)).replace(tzinfo=None)).total_seconds()/60
                    else:
                        break_duration += item.duration_minutes
            else:
                breaks = self.session.query(MSILShopBreaks).filter(MSILShopBreaks.shop_id == shop_id, or_(
                    MSILShopBreaks.start_time > start, MSILShopBreaks.start_time < cur_time))
                for item in breaks:
                    if item.start_time > start or item.end_time < cur_time:
                        break_duration += item.duration_minutes
                    else:
                        break_duration += (cur_datetime - ist_tz.localize(datetime.datetime.combine(
                            cur_date, item.start_time)).replace(tzinfo=None)).total_seconds()/60

            all_breaks = self.session.query(MSILShopBreaks).filter(
                MSILShopBreaks.shop_id == shop_id)
            total_breaks = 0
            if start_time is not None and end_time is not None:
                for each in all_breaks:
                    if start_time.time() < each.start_time < end_time.time():
                        total_breaks = total_breaks + each.duration_minutes
                runtime = (end_time - start_time).total_seconds() / \
                    3600 - total_breaks/60
            else:
                total_breaks = sum(
                    item.duration_minutes for item in all_breaks)
                runtime = (cur_datetime - start_time).total_seconds()/3600

            # runtime = runtime - break_duration/60
            work_hours = work_hours - total_breaks/60

            # return work_hours

            if view == "DAY":
                plan_filter = []
                if material_code:
                    plan_filter.append(MSILPlan.material_code == material_code)
                plan_subquery = self.session.query(MSILPlan.equipment_id.label("plan_eqp_id"), func.sum(MSILPlan.planned_quantity).label("target")) \
                    .filter(MSILPlan.production_date == start_date) \
                    .filter(*plan_filter)\
                    .group_by(MSILPlan.equipment_id) \
                    .subquery()

                machine_telemetry_filter = []
                if material_code:
                    machine_telemetry_filter.append(
                        MSILMachineTelemetry.material_code == material_code)
                telemetry_subquery = self.session.query(MSILMachineTelemetry.equipment_id,
                                                        func.sum(MSILMachineTelemetry.quantity).label(
                                                            "temp_quantity"),
                                                        MSILMachineTelemetry.station_counter_type)\
                    .filter(MSILMachineTelemetry.timestamp >= start_time) \
                    .filter(MSILMachineTelemetry.timestamp <= end_time) \
                    .filter(*machine_telemetry_filter)\
                    .group_by(MSILMachineTelemetry.equipment_id,
                              MSILMachineTelemetry.station_counter_type)\
                    .subquery()
                actual_subquery = self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
                                                     func.sum(telemetry_subquery.c.temp_quantity).label("actual"))\
                    .group_by(telemetry_subquery.c.equipment_id)\
                    .subquery()

                actual_subquery_max = self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
                                                         func.max(telemetry_subquery.c.temp_quantity).label("actual_max"))\
                    .group_by(telemetry_subquery.c.equipment_id)\
                    .subquery()

                # actual_subquery = self.session.query( telemetry_subquery.equipment_id.label("tele_eqp_id"),func.sum(MSILMachineTelemetry.quantity).label("actual"),MSILMachineTelemetry.station_counter_type) \
                #                 .filter(MSILMachineTelemetry.timestamp >= start_time) \
                #                 .filter(MSILMachineTelemetry.timestamp <= end_time) \
                #                 .group_by(MSILMachineTelemetry.equipment_id,MSILMachineTelemetry.station_counter_type) \
                #                 .subquery()

                # downtimes = self.session.query(MSILDowntime.id).filter(func.timezone('-05:30', MSILDowntime.start_time) >= start_time, MSILDowntime.equipment_id=='P008').all()
                # return downtimes

                downtime_filter = []
                if material_code:
                    downtime_filter.append(
                        MSILDowntime.material_code == material_code)
                downtime_subquery = self.session.query(
                    MSILDowntime.equipment_id.label("downtime_eqp_id"),
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'scheduled', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('scheduled'),
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'idle', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('idle'),
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'breakdown', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('breakdown'),
                ).join(
                    MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True
                ).filter(
                    MSILDowntime.start_time >= start_time
                    # ,or_(MSILDowntime.end_time <= cur_datetime, MSILDowntime.end_time.is_(None))
                ).filter(*downtime_filter)\
                    .group_by(
                    MSILDowntime.equipment_id
                ).subquery()

            if view == "CURRENT":
                plan_filter = []
                if material_code:
                    plan_filter.append(MSILPlan.material_code == material_code)

                plan_subquery = self.session.query(MSILPlan.equipment_id.label("plan_eqp_id"), (func.sum(MSILPlan.planned_quantity)*runtime/work_hours).label("target")) \
                    .filter(MSILPlan.production_date == start_date) \
                    .filter(*plan_filter)\
                    .group_by(MSILPlan.equipment_id) \
                    .subquery()

                machine_telemetry_filter = []
                if material_code:
                    machine_telemetry_filter.append(
                        MSILMachineTelemetry.material_code == material_code)

                telemetry_subquery = self.session.query(MSILMachineTelemetry.equipment_id,
                                                        func.sum(MSILMachineTelemetry.quantity).label(
                                                            "temp_quantity"),
                                                        MSILMachineTelemetry.station_counter_type)\
                    .filter(MSILMachineTelemetry.timestamp >= start_time) \
                    .filter(MSILMachineTelemetry.timestamp <= end_time) \
                    .filter(*machine_telemetry_filter)\
                    .group_by(MSILMachineTelemetry.equipment_id,
                              MSILMachineTelemetry.station_counter_type)\
                    .subquery()
                actual_subquery = self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
                                                     func.sum(telemetry_subquery.c.temp_quantity).label("actual"))\
                    .group_by(telemetry_subquery.c.equipment_id)\
                    .subquery()

                actual_subquery_max = self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
                                                         func.max(telemetry_subquery.c.temp_quantity).label("actual_max"))\
                    .group_by(telemetry_subquery.c.equipment_id)\
                    .subquery()

                # actual_subquery = self.session.query( MSILMachineTelemetry.equipment_id.label("tele_eqp_id"),func.sum(MSILMachineTelemetry.quantity).label("actual")) \
                #                 .filter(MSILMachineTelemetry.timestamp >= start_time) \
                #                 .filter(MSILMachineTelemetry.timestamp <= cur_datetime) \
                #                 .group_by(MSILMachineTelemetry.equipment_id) \
                #                 .subquery()

                downtime_filter = []
                if material_code:
                    downtime_filter.append(
                        MSILDowntime.material_code == material_code)
                downtime_subquery = self.session.query(
                    MSILDowntime.equipment_id.label("downtime_eqp_id"),
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'scheduled', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('scheduled'),
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'idle', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('idle'),
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'breakdown', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('breakdown')
                ).join(
                    MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True
                ).filter(
                    MSILDowntime.start_time >= start_time
                    # ,or_(MSILDowntime.end_time <= cur_datetime, MSILDowntime.end_time.is_(None))
                ).filter(*downtime_filter)\
                    .group_by(
                    MSILDowntime.equipment_id
                ).subquery()
            # Included scheduled downtime
            query = self.session.query(self.model_type, func.coalesce(plan_subquery.c.target, 0), func.coalesce(actual_subquery.c.actual, 0), func.coalesce(downtime_subquery.c.idle, 0), func.coalesce(downtime_subquery.c.breakdown, 0)) \
                .filter(self.model_type.shop_id == shop_id, self.model_type.is_deleted == False)
            # print("Query", query)

            if name:
                query = query.filter(self.model_type.name.in_(name))

            if group:
                query = query.filter(self.model_type.equipment_group == group)

            query = query.join(actual_subquery, self.model_type.id == actual_subquery.c.tele_eqp_id, isouter=True) \
                .join(actual_subquery_max, self.model_type.id == actual_subquery_max.c.tele_eqp_id, isouter=True) \
                .join(plan_subquery, self.model_type.id == plan_subquery.c.plan_eqp_id, isouter=True) \
                .join(downtime_subquery, self.model_type.id == downtime_subquery.c.downtime_eqp_id, isouter=True)

            query = query.add_column(
                case(
                    (func.coalesce(plan_subquery.c.target, 0) == 0, 0),
                    else_=(func.coalesce(actual_subquery.c.actual, 0) *
                           100.0) / func.coalesce(plan_subquery.c.target, 0)
                ).label('target_percent')
            )
            query = query.add_column(get_efficiency_by_shop_id(shop_id, downtime_subquery.c.breakdown, downtime_subquery.c.idle, runtime,
                                     downtime_subquery.c.scheduled, actual_prod=column('actual'), planned_prod=(func.coalesce(plan_subquery.c.target, 0))).label('efficiency'))
            query = query.add_column(case(((((runtime*60 - func.coalesce(downtime_subquery.c.breakdown, 0)) / (
                runtime*60 - func.coalesce(downtime_subquery.c.idle, 0))) * 100) < self.model_type.efficiency, 1), else_=0).label('critical'))
            query = query.add_column(get_sph_by_shop_id(shop_id, column(
                'actual'), runtime, downtime_subquery.c.idle, downtime_subquery.c.breakdown, downtime_subquery.c.scheduled).label('sph'))
            query = query.add_column(actual_subquery.c.actual)
            query = query.add_column(column('actual'))
            query = query.add_column(actual_subquery_max.c.actual_max)

            return query.all()

    def get_machine_view(self, shop_id, start_time, end_time, name=None, group=None, view="CURRENT"):

        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        # cur_datetime = ist_tz.localize(datetime.datetime.strptime('2023-10-28 01:00:00','%Y-%m-%d %H:%M:%S')).replace(tzinfo=None)
        cur_time = cur_datetime.time()
        cur_date = cur_datetime.date()

        # if view=="DAY":
        #     runtime = (cur_datetime - shift_start).total_seconds()/60

        with self.session:

            # get the first shift
            # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()

            # calculate the start time of the first shift
            start = start_time

            # if current time is less than start time of the shift, production date is the previous date
            if cur_time < start:
                start_date = cur_date - datetime.timedelta(days=1)
                end_date = cur_date
            else:
                start_date = cur_date
                end_date = cur_date + datetime.timedelta(days=1)

            # start datetime of the production date
            start_time = ist_tz.localize(datetime.datetime.combine(
                start_date, start)).replace(tzinfo=None)

            # get the last shift
            # end_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name.desc()).first()

            # day end is the end of last shift
            end = end_time

            # if the end of last shift is less than the start of first shift, the last shift ends on the next day
            if end < start:
                end_time = ist_tz.localize(datetime.datetime.combine(end_date, end)).replace(
                    minute=30, second=0, microsecond=0, tzinfo=None)
            else:
                end_time = ist_tz.localize(datetime.datetime.combine(cur_date, end)).replace(
                    minute=30, second=0, microsecond=0, tzinfo=None)

            # working hours is the difference between end time of last shift and start time of first shift
            work_hours = (end_time-start_time).total_seconds()/3600
            # return start_time, end_time, cur_datetime, work_hours, cur_time
            greater_than_start = cur_time > start
            break_duration = 0

            if greater_than_start:
                breaks = self.session.query(MSILShopBreaks).filter(
                    MSILShopBreaks.shop_id == shop_id, MSILShopBreaks.start_time < cur_time, MSILShopBreaks.start_time > start)
                for item in breaks:
                    if item.end_time > cur_time:
                        break_duration += (cur_datetime - ist_tz.localize(datetime.datetime.combine(
                            cur_date, item.start_time)).replace(tzinfo=None)).total_seconds()/60
                    else:
                        break_duration += item.duration_minutes
            else:
                breaks = self.session.query(MSILShopBreaks).filter(MSILShopBreaks.shop_id == shop_id, or_(
                    MSILShopBreaks.start_time > start, MSILShopBreaks.start_time < cur_time))
                for item in breaks:
                    if item.start_time > start or item.end_time < cur_time:
                        break_duration += item.duration_minutes
                    else:
                        break_duration += (cur_datetime - ist_tz.localize(datetime.datetime.combine(
                            cur_date, item.start_time)).replace(tzinfo=None)).total_seconds()/60

            all_breaks = self.session.query(MSILShopBreaks).filter(
                MSILShopBreaks.shop_id == shop_id)
            total_breaks = sum(item.duration_minutes for item in all_breaks)

            runtime = (cur_datetime - start_time).total_seconds()/3600
            # runtime = runtime - break_duration/60
            work_hours = work_hours - total_breaks/60
            print(start_time, end_time, runtime, work_hours)
            print("cur_datetime", cur_datetime, total_breaks/60)
            plan_subquery = self.session.query(MSILPlan.equipment_id.label("plan_eqp_id"), (func.sum(MSILPlan.planned_quantity)).label("day_target")) \
                .filter(MSILPlan.production_date == start_date) \
                .group_by(MSILPlan.equipment_id) \
                .subquery()

            telemetry_subquery = self.session.query(MSILMachineTelemetry.equipment_id,
                                                    func.sum(MSILMachineTelemetry.quantity).label(
                                                        "temp_quantity"),
                                                    MSILMachineTelemetry.station_counter_type)\
                .filter(MSILMachineTelemetry.timestamp >= start_time) \
                .filter(MSILMachineTelemetry.timestamp <= end_time) \
                .group_by(MSILMachineTelemetry.equipment_id,
                          MSILMachineTelemetry.station_counter_type)\
                .subquery()
            actual_subquery = self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
                                                 func.sum(telemetry_subquery.c.temp_quantity).label("actual"))\
                .group_by(telemetry_subquery.c.equipment_id)\
                .subquery()

            # sph_subquery =  self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
            #                                           case((self.model_type.equipment_group.ilike(f"Blanking%"),
            #                                         func.sum(telemetry_subquery.c.temp_quantity)),
            #                                         else_ =func.max(telemetry_subquery.c.temp_quantity)).label("no_of_stroke"))\
            #                                     .group_by(telemetry_subquery.c.equipment_id,
            #                                               self.model_type.equipment_group)\
            #                                 .subquery()

            sph_subquery = self.session.query(telemetry_subquery.c.equipment_id.label("tele_eqp_id"),
                                              func.max(telemetry_subquery.c.temp_quantity).label("no_of_stroke"))\
                .group_by(telemetry_subquery.c.equipment_id)\
                .subquery()

            # actual_subquery = self.session.query( MSILMachineTelemetry.equipment_id.label("tele_eqp_id"),func.sum(MSILMachineTelemetry.quantity).label("actual")) \
            #                 .filter(MSILMachineTelemetry.timestamp >= start_time) \
            #                 .filter(MSILMachineTelemetry.timestamp <= cur_datetime) \
            #                 .group_by(MSILMachineTelemetry.equipment_id) \
            #                 .subquery()

            downtime_subquery = self.session.query(
                MSILDowntime.equipment_id.label("downtime_eqp_id"),
                func.sum(
                    case(
                        (MSILDowntimeReasons.reason_type == 'scheduled', func.coalesce(
                            case(
                                (MSILDowntime.end_time.is_(None),
                                 (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                else_=MSILDowntime.duration
                            ),
                            0
                        )),
                        else_=0
                    )
                ).label('scheduled'),
                func.sum(
                    case(
                        (MSILDowntimeReasons.reason_type == 'idle', func.coalesce(
                            case(
                                (MSILDowntime.end_time.is_(None),
                                 (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                else_=MSILDowntime.duration
                            ),
                            0
                        )),
                        else_=0
                    )
                ).label('idle'),
                func.sum(
                    case(
                        (MSILDowntimeReasons.reason_type == 'breakdown', func.coalesce(
                            case(
                                (MSILDowntime.end_time.is_(None),
                                 (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                else_=MSILDowntime.duration
                            ),
                            0
                        )),
                        else_=0
                    )
                ).label('breakdown')
            ).join(
                MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True
            ).filter(
                MSILDowntime.start_time >= start_time
                # ,or_(MSILDowntime.end_time <= cur_datetime, MSILDowntime.end_time.is_(None))
            ).group_by(
                MSILDowntime.equipment_id
            ).subquery()
        # Included scheduled downtime

            active_downtime_subquery = self.session.query(
                MSILDowntime.equipment_id.label("active_downtime_eqp_id"),
                func.sum(
                    case(
                        (MSILDowntimeReasons.reason_type == 'scheduled', func.coalesce(
                            case(
                                (MSILDowntime.end_time.is_(None),
                                 (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                else_=MSILDowntime.duration
                            ),
                            0
                        )),
                        else_=0
                    )
                ).label('active_scheduled'),
                func.sum(
                    case(
                        (MSILDowntimeReasons.reason_type == 'idle', func.coalesce(
                            case(
                                (MSILDowntime.end_time.is_(None),
                                 (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                else_=MSILDowntime.duration
                            ),
                            0
                        )),
                        else_=0
                    )
                ).label('active_idle'),
                func.sum(
                    case(
                        (MSILDowntimeReasons.reason_type == 'breakdown', func.coalesce(
                            case(
                                (MSILDowntime.end_time.is_(None),
                                 (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                else_=MSILDowntime.duration
                            ),
                            0
                        )),
                        else_=0
                    )
                ).label('active_breakdown')
            ).join(
                MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True
            ).filter(
                MSILDowntime.start_time >= start_time,
                MSILDowntime.end_time.is_(None)
                # ,or_(MSILDowntime.end_time <= cur_datetime, MSILDowntime.end_time.is_(None))
            ).group_by(
                MSILDowntime.equipment_id
            ).subquery()

            query = self.session.query(self.model_type, func.coalesce(plan_subquery.c.day_target, 0), func.coalesce(actual_subquery.c.actual, 0), func.coalesce(downtime_subquery.c.idle, 0), func.coalesce(downtime_subquery.c.breakdown, 0), func.coalesce(active_downtime_subquery.c.active_breakdown, 0), func.coalesce(active_downtime_subquery.c.active_idle, 0), func.coalesce(active_downtime_subquery.c.active_scheduled, 0), func.coalesce(sph_subquery.c.no_of_stroke, 0)) \
                .filter(self.model_type.shop_id == shop_id, self.model_type.is_deleted == False)
            # print("Query", query)

            if name:
                query = query.filter(self.model_type.name.in_(name))

            if group:
                query = query.filter(self.model_type.equipment_group == group)

            query = query.join(actual_subquery, self.model_type.id == actual_subquery.c.tele_eqp_id, isouter=True) \
                .join(sph_subquery, self.model_type.id == sph_subquery.c.tele_eqp_id, isouter=True) \
                .join(plan_subquery, self.model_type.id == plan_subquery.c.plan_eqp_id, isouter=True) \
                .join(downtime_subquery, self.model_type.id == downtime_subquery.c.downtime_eqp_id, isouter=True) \
                .join(active_downtime_subquery, self.model_type.id == active_downtime_subquery.c.active_downtime_eqp_id, isouter=True)

            query = query.add_column(
                case(
                    (func.coalesce(plan_subquery.c.day_target, 0) == 0, 0),
                    else_=(func.coalesce(actual_subquery.c.actual, 0) *
                           100.0) / func.coalesce(plan_subquery.c.day_target, 0)
                ).label('target_percent')
            )
            query = query.add_column(get_efficiency_by_shop_id(shop_id, downtime_subquery.c.breakdown,
                                     downtime_subquery.c.idle, runtime, downtime_subquery.c.scheduled).label('efficiency'))
            query = query.add_column(get_sph_by_shop_id(shop_id, column(
                'no_of_stroke'), runtime, downtime_subquery.c.idle, downtime_subquery.c.breakdown, downtime_subquery.c.scheduled).label('sph'))
            query = query.add_column(actual_subquery.c.actual)
            query = query.add_column(column('actual'))
            return query.all(), runtime, work_hours

    def actual_graph(self, shop_id, start_time, end_time, name=None):

        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        cur_date = cur_datetime.date()

        # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
        start = start_time
        start_time = ist_tz.localize(datetime.datetime.combine(
            cur_date, start)).replace(tzinfo=None)

        # end_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name.desc()).first()
        next_date = cur_date + datetime.timedelta(days=1)
        end = end_time
        if end < start:
            end_time = ist_tz.localize(datetime.datetime.combine(
                next_date, end)).replace(tzinfo=None)
        else:
            end_time = ist_tz.localize(datetime.datetime.combine(
                cur_date, end)).replace(tzinfo=None)

        with self.session:

            subquery = (
                self.session.query(func.generate_series(
                    start_time, cur_datetime, text("'1 minute'")).label('minute')).subquery()
            )

            telemetry_query = self.session.query((func.date_trunc('minutes', MSILMachineTelemetry.timestamp)).label('minute_val'), (func.sum(MSILMachineTelemetry.quantity)).label('quantity')) \
                .join(MSILEquipment, MSILMachineTelemetry.equipment_id == MSILEquipment.id) \
                .filter(MSILEquipment.name == name,
                        MSILEquipment.shop_id == shop_id,
                        MSILMachineTelemetry.timestamp > start_time) \
                .group_by('minute_val').all()

            telemetry_query = list(telemetry_query)
            timestamps_and_quantities = []
            current_quantity = 0

            current_timestamp = start_time
            telemetry_data = {item[0].strftime(
                "%Y-%m-%d %H:%M"): item[1] for item in telemetry_query}
            while current_timestamp < cur_datetime:
                timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
                    '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 2)})
                current_quantity += telemetry_data.get(
                    current_timestamp.strftime("%Y-%m-%d %H:%M"), 0)
                # for item in telemetry_query:
                #     if item[0].strftime("%Y-%m-%d %H:%M")==current_timestamp.strftime("%Y-%m-%d %H:%M"):
                #         current_quantity += item[1]

                # print(item[0])
                # print(current_timestamp)

                current_timestamp += datetime.timedelta(minutes=1)

            timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
                '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 2)})
            return timestamps_and_quantities

    def target_graph(self, shop_id, start_time, end_time, name=None, view="DAY"):
        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz)
        cur_time = cur_datetime.time()
        cur_date = cur_datetime.date()

        # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
        start = start_time
        if cur_time < start:
            start_date = cur_date - datetime.timedelta(days=1)
            end_date = cur_date
        else:
            start_date = cur_date
            end_date = cur_date + datetime.timedelta(days=1)
        start_time = ist_tz.localize(
            datetime.datetime.combine(start_date, start))

        # end_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name.desc()).first()

        end = end_time
        if end < start:
            end_time = ist_tz.localize(datetime.datetime.combine(
                end_date, end)).replace(minute=30, second=0, microsecond=0)
        else:
            end_time = ist_tz.localize(datetime.datetime.combine(
                cur_date, end)).replace(minute=30, second=0, microsecond=0)

        work_hours = (end_time-start_time).total_seconds()/3600

        greater_than_start = cur_time > start
        break_duration = 0

        if greater_than_start:
            breaks = self.session.query(MSILShopBreaks).filter(
                MSILShopBreaks.shop_id == shop_id, MSILShopBreaks.start_time < cur_time, MSILShopBreaks.start_time > start)
            for item in breaks:
                if item.end_time > cur_time:
                    break_duration += (cur_datetime - ist_tz.localize(
                        datetime.datetime.combine(cur_date, item.start_time))).total_seconds()/60
                else:
                    break_duration += item.duration_minutes
        else:
            breaks = self.session.query(MSILShopBreaks).filter(MSILShopBreaks.shop_id == shop_id, or_(
                MSILShopBreaks.start_time > start, MSILShopBreaks.start_time < cur_time))
            for item in breaks:
                if item.start_time > start or item.end_time < cur_time:
                    break_duration += item.duration_minutes
                else:
                    break_duration += (cur_datetime - ist_tz.localize(
                        datetime.datetime.combine(cur_date, item.start_time))).total_seconds()/60

        total_breaks = sum(item.duration_minutes for item in breaks)

        equipment = self.session.query(MSILEquipment).filter(
            MSILEquipment.shop_id == shop_id,
            MSILEquipment.name == name
        ).all()

        downtime = self.session.query(MSILShopBreaks).filter(
            MSILShopBreaks.shop_id == shop_id)

        plan = self.session.query(MSILPlan).filter(
            MSILPlan.equipment_id.in_([e.id for e in equipment]),
            MSILPlan.shop_id == shop_id,
            MSILPlan.production_date == cur_date
        ).all()

        total_downtime_duration = sum(
            item.duration_minutes for item in downtime)
        remaining_working_hours = work_hours - (total_downtime_duration / 60)
        total_planned_quantity = sum(item.planned_quantity for item in plan)

        timestamps_and_quantities = []
        current_timestamp = start_time
        current_quantity = 0

        downtime_intervals = []

        for dt in downtime:
            if dt.start_time < start:
                break_start = ist_tz.localize(
                    datetime.datetime.combine(end_date, dt.start_time))
            else:
                break_start = ist_tz.localize(
                    datetime.datetime.combine(start_date, dt.start_time))
            if dt.end_time < start:
                break_end = ist_tz.localize(
                    datetime.datetime.combine(end_date, dt.end_time))
            else:
                break_end = ist_tz.localize(
                    datetime.datetime.combine(start_date, dt.end_time))
            downtime_intervals.append((break_start, break_end))

        # return remaining_working_hours

        rate_per_minute = (total_planned_quantity /
                           remaining_working_hours) / 60

        if view == 'DAY':
            time_limit = end_time
        elif view == 'CURRENT':
            time_limit = cur_datetime

        while current_timestamp < time_limit:
            if current_quantity < total_planned_quantity:
                timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
                    '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 0)})

            # Check if the current timestamp is within any downtime interval
            if any(start <= current_timestamp <= end for start, end in downtime_intervals):
                # Inside downtime, quantity remains constant
                pass
            elif current_quantity < total_planned_quantity:
                current_quantity += rate_per_minute
                # current_quantity += 1

            current_timestamp += datetime.timedelta(minutes=1)

        timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
            '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 0)})
        return timestamps_and_quantities

    def equipment_ids(self, shop_id):
        equipment_dict = {}
        with self.session:
            equipments = self.session.query(MSILEquipment).filter(
                MSILEquipment.shop_id == shop_id).all()
            for equipment in equipments:
                equipment_dict[equipment.name] = equipment.id
            return equipment_dict

    def check_for_machines(self, machine_names, shop_id):
        with self.session:
            result_dict = {}
            results = self.session.query(self.model_type.name, self.model_type.id).filter(
                self.model_type.shop_id == shop_id).where(self.model_type.name.in_(machine_names)).distinct().all()
            for item in results:
                result_dict[item[0]] = item[1]
            return result_dict

    def soft_delete_equipments(self, eqp_ids, shop_id):
        with self.session:
            to_be_deleted = self.session.query(self.model_type).filter(
                self.model_type.id.in_(eqp_ids), self.model_type.shop_id == shop_id).all()
            for item in to_be_deleted:
                item.is_deleted = True
                self.session.merge(item)
            self.session.commit()

    def get_equipment_by_id(self, equipment_id):
        with self.session:
            query = self.session.query(MSILEquipment).filter(
                MSILEquipment.id == equipment_id)
            equipment = query.first()
            return equipment if equipment else None

    def actual_graph_new(self, shop_id, start_time, end_time, name=None):

        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        cur_date = cur_datetime.date()

        # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
        start = start_time
        start_time = ist_tz.localize(datetime.datetime.combine(
            cur_date, start)).replace(tzinfo=None)

        # end_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name.desc()).first()
        next_date = cur_date + datetime.timedelta(days=1)
        end = end_time
        if end < start:
            end_time = ist_tz.localize(datetime.datetime.combine(
                next_date, end)).replace(tzinfo=None)
        else:
            end_time = ist_tz.localize(datetime.datetime.combine(
                cur_date, end)).replace(tzinfo=None)

        with self.session:

            subquery = (
                self.session.query(func.generate_series(
                    start_time, cur_datetime, text("'1 minute'")).label('minute')).subquery()
            )

            telemetry_query = self.session.query((func.date_trunc('minutes', MSILMachineTelemetry.timestamp)).label('minute_val'), (func.sum(MSILMachineTelemetry.quantity)).label('quantity')) \
                .join(MSILEquipment, MSILMachineTelemetry.equipment_id == MSILEquipment.id) \
                .filter(MSILEquipment.shop_id == shop_id,
                        MSILMachineTelemetry.timestamp > start_time)
            if name != None:
                telemetry_query = telemetry_query.filter(
                    MSILEquipment.name == name)
            telemetry_query.group_by('minute_val').all()

            telemetry_query = list(telemetry_query)
            timestamps_and_quantities = []
            current_quantity = 0

            current_timestamp = start_time
            telemetry_data = {item[0].strftime(
                "%Y-%m-%d %H:%M"): item[1] for item in telemetry_query}
            while current_timestamp < cur_datetime:
                timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
                    '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 2)})
                current_quantity += telemetry_data.get(
                    current_timestamp.strftime("%Y-%m-%d %H:%M"), 0)
                # for item in telemetry_query:
                #     if item[0].strftime("%Y-%m-%d %H:%M")==current_timestamp.strftime("%Y-%m-%d %H:%M"):
                #         current_quantity += item[1]

                # print(item[0])
                # print(current_timestamp)

                current_timestamp += datetime.timedelta(minutes=1)

            timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
                '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 2)})
            return timestamps_and_quantities

    def target_graph_new(self, shop_id, start_time, end_time, name=None, view="DAY"):
        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz)
        cur_time = cur_datetime.time()
        cur_date = cur_datetime.date()

        # start_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name).first()
        start = start_time
        if cur_time < start:
            start_date = cur_date - datetime.timedelta(days=1)
            end_date = cur_date
        else:
            start_date = cur_date
            end_date = cur_date + datetime.timedelta(days=1)
        start_time = ist_tz.localize(
            datetime.datetime.combine(start_date, start))

        # end_query = self.session.query(MSILShift).filter(MSILShift.shop_id==shop_id).order_by(MSILShift.shift_name.desc()).first()

        end = end_time
        if end < start:
            end_time = ist_tz.localize(datetime.datetime.combine(
                end_date, end)).replace(minute=30, second=0, microsecond=0)
        else:
            end_time = ist_tz.localize(datetime.datetime.combine(
                cur_date, end)).replace(minute=30, second=0, microsecond=0)

        work_hours = (end_time-start_time).total_seconds()/3600

        greater_than_start = cur_time > start
        break_duration = 0

        if greater_than_start:
            breaks = self.session.query(MSILShopBreaks).filter(
                MSILShopBreaks.shop_id == shop_id, MSILShopBreaks.start_time < cur_time, MSILShopBreaks.start_time > start)
            for item in breaks:
                if item.end_time > cur_time:
                    break_duration += (cur_datetime - ist_tz.localize(
                        datetime.datetime.combine(cur_date, item.start_time))).total_seconds()/60
                else:
                    break_duration += item.duration_minutes
        else:
            breaks = self.session.query(MSILShopBreaks).filter(MSILShopBreaks.shop_id == shop_id, or_(
                MSILShopBreaks.start_time > start, MSILShopBreaks.start_time < cur_time))
            for item in breaks:
                if item.start_time > start or item.end_time < cur_time:
                    break_duration += item.duration_minutes
                else:
                    break_duration += (cur_datetime - ist_tz.localize(
                        datetime.datetime.combine(cur_date, item.start_time))).total_seconds()/60

        total_breaks = sum(item.duration_minutes for item in breaks)

        equipment = self.session.query(MSILEquipment).filter(
            MSILEquipment.shop_id == shop_id
        )

        if name != None:
            equipment = equipment.filter(MSILEquipment.name == name)

        equipment = equipment.all()

        downtime = self.session.query(MSILShopBreaks).filter(
            MSILShopBreaks.shop_id == shop_id)

        plan = self.session.query(MSILPlan).filter(
            MSILPlan.equipment_id.in_([e.id for e in equipment]),
            MSILPlan.shop_id == shop_id,
            MSILPlan.production_date == cur_date
        ).all()

        total_downtime_duration = sum(
            item.duration_minutes for item in downtime)
        remaining_working_hours = work_hours - (total_downtime_duration / 60)
        total_planned_quantity = sum(item.planned_quantity for item in plan)

        timestamps_and_quantities = []
        current_timestamp = start_time
        current_quantity = 0

        downtime_intervals = []

        for dt in downtime:
            if dt.start_time < start:
                break_start = ist_tz.localize(
                    datetime.datetime.combine(end_date, dt.start_time))
            else:
                break_start = ist_tz.localize(
                    datetime.datetime.combine(start_date, dt.start_time))
            if dt.end_time < start:
                break_end = ist_tz.localize(
                    datetime.datetime.combine(end_date, dt.end_time))
            else:
                break_end = ist_tz.localize(
                    datetime.datetime.combine(start_date, dt.end_time))
            downtime_intervals.append((break_start, break_end))

        # return remaining_working_hours

        rate_per_minute = (total_planned_quantity /
                           remaining_working_hours) / 60

        if view == 'CURRENT_SHIFT':
            time_limit = end_time
        elif view == 'CURRENT':
            time_limit = cur_datetime

        while current_timestamp < time_limit:
            if current_quantity < total_planned_quantity:
                timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
                    '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 0)})

            # Check if the current timestamp is within any downtime interval
            if any(start <= current_timestamp <= end for start, end in downtime_intervals):
                # Inside downtime, quantity remains constant
                pass
            elif current_quantity < total_planned_quantity:
                current_quantity += rate_per_minute
                # current_quantity += 1

            current_timestamp += datetime.timedelta(minutes=1)

        timestamps_and_quantities.append({'timestamp': current_timestamp.strftime(
            '%Y-%m-%d %H:%M:00'), 'quantity': round(current_quantity, 0)})
        return timestamps_and_quantities

    def get_machine_actual_plan_stroke_breakdown_and_die_change_data(self, shop_id, start_time, end_time, machine_id=None):
        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        cur_time = cur_datetime.time()
        cur_date = cur_datetime.date()

        with self.session:

            start = start_time

            # if current time is less than start time of the shift, production date is the previous date
            if cur_time < start:
                start_date = cur_date - datetime.timedelta(days=1)
                end_date = cur_date
            else:
                start_date = cur_date
                end_date = cur_date + datetime.timedelta(days=1)

            # start datetime of the production date
            start_time = ist_tz.localize(datetime.datetime.combine(
                start_date, start)).replace(tzinfo=None)
            end = end_time

            # if the end of last shift is less than the start of first shift, the last shift ends on the next day
            if end < start:
                end_time = ist_tz.localize(datetime.datetime.combine(end_date, end)).replace(
                    minute=30, second=0, microsecond=0, tzinfo=None)
            else:
                end_time = ist_tz.localize(datetime.datetime.combine(cur_date, end)).replace(
                    minute=30, second=0, microsecond=0, tzinfo=None)

            plan_query = self.session.query((func.sum(MSILPlan.planned_quantity)).label("day_target")) \
                .filter(MSILPlan.production_date == start_date) \
                .filter(MSILPlan.shop_id == shop_id)

            if machine_id != None:
                plan_query = plan_query.filter(
                    MSILPlan.equipment_id == machine_id)

            plan_query = plan_query.all()

            actual_query = self.session.query(func.sum(MSILMachineTelemetry.quantity).label("actual_quantity"))\
                .filter(MSILMachineTelemetry.timestamp >= start_time) \
                .filter(MSILMachineTelemetry.timestamp <= end_time)

            if machine_id != None:
                actual_query = actual_query.filter(
                    MSILMachineTelemetry.equipment_id == machine_id)

            actual_query = actual_query.all()

            stroke_subquery = self.session.query(func.sum(MSILMachineTelemetry.quantity).label("station_quantity"),
                                                 MSILMachineTelemetry.station_counter_type)\
                .filter(MSILMachineTelemetry.timestamp >= start_time) \
                .filter(MSILMachineTelemetry.timestamp <= end_time) \
                .group_by(MSILMachineTelemetry.station_counter_type)\
                .subquery()

            if machine_id != None:
                stroke_subquery = stroke_subquery.filter(
                    MSILMachineTelemetry.equipment_id == machine_id)

            total_stroke = self.session.query(
                func.max(stroke_subquery.c.station_quantity).label("total_stroke"))
            total_stroke = total_stroke.all()

            if machine_id:
                downtime_query = self.session.query(
                    func.sum(
                        case(
                            (MSILDowntimeReasons.reason_type == 'breakdown', func.coalesce(
                                case(
                                    (MSILDowntime.end_time.is_(None),
                                     (func.extract('epoch', cur_datetime) - func.extract('epoch', MSILDowntime.start_time)) / 60),
                                    else_=MSILDowntime.duration
                                ),
                                0
                            )),
                            else_=0
                        )
                    ).label('breakdown')
                ).join(
                    MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True
                ).filter(
                    MSILDowntime.start_time >= start_time,
                    MSILDowntime.equipment_id == machine_id,
                    MSILDowntime.shop_id == shop_id
                ).all()

                print(downtime_query)

                die_change_query = self.session.query(MSILDowntime.start_time, MSILDowntime.end_time) \
                    .join(
                    MSILDowntimeReasons, MSILDowntime.reason_id == MSILDowntimeReasons.id, isouter=True
                ).filter(
                    MSILDowntime.start_time >= start_time,
                    MSILDowntime.equipment_id == machine_id,
                    MSILDowntime.shop_id == shop_id,
                    MSILDowntimeReasons.reason == 'Die change'
                ).all()

                print(die_change_query)
            print(plan_query, actual_query, total_stroke)

    def get_equipment_by_shop(self, shop_id):
        """
        Get all equipment by shop_id.
        """
        with self.session:
            results = self.session.query(self.model_type.id) \
                .filter(self.model_type.shop_id == shop_id) \
                .distinct() \
                .all()
            return [result[0] for result in results]
