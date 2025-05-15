import pytz
from app.modules.PSM.repositories.repository import Repository
from app.modules.PSM.repositories.models.msil_downtime import MSILDowntime
from app.modules.PSM.repositories.models.msil_downtime_reason import MSILDowntimeReasons
from app.modules.PSM.repositories.models.msil_downtime_remark import MSILDowntimeRemarks
from app.modules.PSM.repositories.models.msil_machine_telemetry import MSILMachineTelemetry
from app.modules.PSM.repositories.models.msil_equipment import MSILEquipment
from app.modules.PSM.repositories.models.msil_model import MSILModel
from app.modules.PSM.repositories.models.msil_part import MSILPart
from app.modules.PSM.repositories.models.msil_shift import MSILShift
from app.modules.PSM.repositories.models.msil_production import MSILProduction
import math
from sqlalchemy import (
    extract,
    func,
    desc,
    case,
    and_,
    cast,
    or_
)
from sqlalchemy.orm import Session, aliased
import datetime

ist_tz = pytz.timezone('Asia/Kolkata')
from app.modules.PSM.services.shift_util import get_shift


class MSILDowntimeRepository(Repository):
    """

    """

    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILDowntime
        self.remark_model = MSILDowntimeRemarks

    def get_remarks(self, shop_id, machine_list=None,
                    model_list=None, part_name_list=None,
                    start_time=None, end_time=None, start=None, end=None, shift=None,
                    reason=None, remarks=None, limit=10, offset=0):
        """Get sorted plans from db
        Default sort : By date, priority, status

        Returns:
            model_list: list of models
        """
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        with self.session:

            input_1_part = aliased(MSILPart)
            input_2_part = aliased(MSILPart)
            query = self.session.query(self.model_type, MSILEquipment.name, MSILModel.model_name,
                                       input_1_part.part_name, MSILDowntimeReasons.reason, MSILDowntimeRemarks.remark,
                                       case(
                                           (MSILDowntime.end_time.is_(None),
                                            (func.extract('epoch', cur_datetime) - func.extract('epoch',
                                                                                                MSILDowntime.start_time)) / 60.0
                                            ),
                                           else_=MSILDowntime.duration).label('new_duration')
                                       , input_2_part.part_name) \
                .filter(self.model_type.shop_id == shop_id)

            if (start_time):
                query = query.filter(self.model_type.start_time >= (start_time))

            if (end_time):
                query = query.filter(self.model_type.end_time <= (end_time))

            if (start):
                query = query.filter(case(
                    (MSILDowntime.end_time.is_(None),
                     (func.extract('epoch', cur_datetime) - func.extract('epoch',
                                                                         MSILDowntime.start_time)) / 60.0),
                    else_=MSILDowntime.duration) > start)

            if (end):
                query = query.filter(case(
                    (MSILDowntime.end_time.is_(None),
                     (func.extract('epoch', cur_datetime) - func.extract('epoch',
                                                                         MSILDowntime.start_time)) / 60.0),
                    else_=MSILDowntime.duration) <= end)

            if (shift):
                query = query.filter(self.model_type.shift.in_(shift))

            query = query.join(MSILModel, self.model_type.model_id == MSILModel.id, isouter=True)

            if (model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))

            query = query.join(input_1_part, self.model_type.material_code == input_1_part.material_code, isouter=True)
            query = query.join(input_2_part, self.model_type.part_2_material_code == input_2_part.material_code,
                               isouter=True)

            if (part_name_list):
                query = query.filter(
                    or_(input_1_part.part_name.in_(part_name_list), input_2_part.part_name.in_(part_name_list)))

            query = query.join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id)

            if (machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))

            query = query.join(MSILDowntimeReasons, self.model_type.reason_id == MSILDowntimeReasons.id)

            if (reason):
                query = query.filter(MSILDowntimeReasons.reason.in_(reason))

            query = query.join(MSILDowntimeRemarks, self.model_type.remark_id == MSILDowntimeRemarks.id, isouter=True)

            if (remarks):
                query = query.filter(MSILDowntimeRemarks.remark.in_(remarks))

            return query.order_by(desc(self.model_type.start_time)) \
                .limit(limit) \
                .offset(offset) \
                .all()

    def get_unique_downtime_filters(self, shop_id):
        with self.session:
            # subquery_1 = self.session.query(MSILPart.part_name.label('part_name'),MSILPart.material_code.label('material_code')) \
            # .select_from(self.model_type) \
            # .join(MSILPart, self.model_type.material_code == MSILPart.material_code)
            # subquery_2 = self.session.query(MSILPart.part_name.label('part_name'),MSILPart.material_code.label('material_code')) \
            # .select_from(self.model_type) \
            # .join(MSILPart, self.model_type.part_2_material_code == MSILPart.material_code)
            # combine = subquery_1.union_all(subquery_2).subquery()
            # return combine
            # part_query = self.session.query(combine.c.material_code).subquery()
            query = (
                self.session.query(
                    MSILEquipment.equipment_group, MSILEquipment.name, MSILModel.model_name, MSILPart.part_name,
                    MSILDowntimeReasons.reason, MSILDowntimeRemarks.remark, )
                .select_from(self.model_type)
                .filter(self.model_type.shop_id == shop_id)
                .join(MSILModel, self.model_type.model_id == MSILModel.id)
                .join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id)
                .join(MSILDowntimeReasons, self.model_type.reason_id == MSILDowntimeReasons.id)
                # .join(combine, self.model_type.material_code == combine.c.part_2_material_code)
                .join(MSILDowntimeRemarks, self.model_type.remark_id == MSILDowntimeRemarks.id, isouter=True)
            )
            # return combine
            query_1 = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code)
            query_2 = query.join(MSILPart, self.model_type.part_2_material_code == MSILPart.material_code)
            combine = query_1.union_all(query_2)

            return combine.distinct().all()

    def end_downtime(self, shop_id, equipment_id, end_time):
        with self.session:
            downtimes = self.filter_by_many(shop_id=shop_id, equipment_id=equipment_id, end_time=None)
            for downtime in downtimes:
                downtime.end_time = end_time
                # .duration
                downtime_seconds = (downtime.end_time - downtime.start_time).total_seconds()
                downtime_minutes = downtime_seconds // 60
                remaining_seconds = (downtime_seconds % 60) / 100.0
                downtime_duration = downtime_minutes + round(remaining_seconds, 2)
                formatted_downtime_duration = "{:.2f}".format(downtime_duration)
                downtime.duration = formatted_downtime_duration
                self.session.merge(downtime)
            self.commit()

    def update_downtime(self, downtimes, reason_id):
        with self.session:
            for downtime in downtimes:
                downtime.reason_id = reason_id
                self.session.merge(downtime)
            self.session.commit()

    def new_remark_status(self, id, remarks, comment, user, shop):
        with self.session:
            result = self.session.query(self.model_type) \
                .join(MSILDowntimeReasons, self.model_type.reason_id == MSILDowntimeReasons.id) \
                .filter(self.model_type.id == id) \
                .filter(self.model_type.shop_id == shop).first()

            if result:
                id_remark = self.session.query(self.remark_model) \
                    .filter(self.remark_model.reason_id == str(result.reason_id)) \
                    .filter(self.remark_model.remark == str(remarks)).first()

                if id_remark:  # Check if id_remark is not None
                    result.remark_id = id_remark.id
                    result.comment = comment
                    result.updated_by = user
                    self.commit()

                    result_dict = {
                        'id': result.id,
                        'reason_id': result.reason_id,
                        'remark_id': result.remark_id,
                        'comment': result.comment,
                        'Updated_By': result.updated_by
                    }
                    return result_dict
                else:
                    # Handle case where no matching remark is found
                    return {
                        'error': f'No matching remark found for reason_id {result.reason_id} and remark "{remarks}".'}
            else:
                # Handle case where no matching downtime record is found
                return {'error': f'No matching downtime record found for id {id} and shop_id {shop}.'}

    def check_downtime(self, shop, cur_date, shift_param, end_times=[]):
        # end_times = []
        ist_tz = pytz.timezone('Asia/Kolkata')
        cur_minute = datetime.datetime.now(ist_tz).replace(second=0, microsecond=0, tzinfo=None)
        cur_shift = shift_param
        prev_minute = cur_minute - datetime.timedelta(minutes=1)
        # downtime reason for shop
        downtime_reason = self.session.query(MSILDowntimeReasons).filter(MSILDowntimeReasons.shop_id == shop,
                                                                         MSILDowntimeReasons.reason_type == "breakdown",
                                                                         MSILDowntimeReasons.reason == "No parts produced").first()

        with self.session:

            # shifts = self.session.query(MSILShift).filter(MSILShift.shop_id==shop).all()
            # for item in shifts:
            #     et = item.shift_end_timing
            #     et = datetime.time(et.hour, et.minute)
            #     end_times.append(et)

            equipments = self.session.query(MSILEquipment).filter(MSILEquipment.is_deleted.isnot(True)).filter(MSILEquipment.shop_id == shop).all()
            # return equipments
            for eqp in equipments:

                # telemetry_result = self.session.query(MSILMachineTelemetry) \
                #                     .filter(MSILMachineTelemetry.equipment_id==eqp.id,
                #                             func.date_trunc('minutes', MSILMachineTelemetry.timestamp)==cur_minute).first()
                telemetry_result = self.session.query(MSILMachineTelemetry) \
                    .filter(MSILMachineTelemetry.equipment_id == eqp.id,
                            MSILMachineTelemetry.timestamp >= prev_minute).first()
                # print(telemetry_result)

                equipment_item = self.session.query(MSILEquipment).filter(MSILEquipment.id == eqp.id).first()
                downtime_item = self.session.query(self.model_type) \
                    .filter(self.model_type.equipment_id == eqp.id, \
                            self.model_type.end_time == None).order_by(self.model_type.start_time.desc()).first()
                # self.model_type.start_time <= cur_minute,

                for et in end_times:
                    if downtime_item and cur_minute.time() == et:
                        downtime_item.end_time = cur_minute.strftime("%Y-%m-%d %H:%M:%S")
                        downtime_start = ist_tz.localize(downtime_item.start_time).replace(tzinfo=None)
                        # downtime_item.duration = round((cur_minute - downtime_start).total_seconds() / 60.0, 2)
                        downtime_seconds = (cur_minute - downtime_start).total_seconds()
                        downtime_minutes = downtime_seconds // 60
                        remaining_seconds = (downtime_seconds % 60) / 100.0
                        downtime_duration = downtime_minutes + round(remaining_seconds, 2)
                        formatted_downtime_duration = "{:.2f}".format(downtime_duration)

                        downtime_item.duration = float(formatted_downtime_duration)
                        # int(math.ceil((cur_minute-downtime_start).total_seconds()/60))

                production_item = self.session.query(MSILProduction).filter(MSILProduction.equipment_id == eqp.id,
                                                                            MSILProduction.date == cur_date).first()

                if telemetry_result:
                    equipment_item.status = "RUNNING"
                    if downtime_item and downtime_item.start_time < prev_minute:
                        downtime_item.end_time = prev_minute.strftime("%Y-%m-%d %H:%M:%S")
                        downtime_start = ist_tz.localize(downtime_item.start_time).replace(tzinfo=None)
                        # downtime_item.duration = round((prev_minute - downtime_start).total_seconds() / 60.0, 2)
                        downtime_seconds = (prev_minute - downtime_start).total_seconds()
                        downtime_minutes = downtime_seconds // 60
                        remaining_seconds = (downtime_seconds % 60) / 100.0
                        downtime_duration = downtime_minutes + round(remaining_seconds, 2)
                        formatted_downtime_duration = "{:.2f}".format(downtime_duration)
                        downtime_item.duration = float(formatted_downtime_duration)
                        # int(math.ceil((prev_minute-downtime_start).total_seconds()/60))
                        self.session.merge(downtime_item)

                else:
                    if downtime_item:
                        reason_item = self.session.query(MSILDowntimeReasons).filter(
                            MSILDowntimeReasons.id == downtime_item.reason_id).first()
                        if reason_item.reason_type == 'breakdown':
                            equipment_item.status = "BREAKDOWN"
                        elif reason_item.reason_type == 'idle':
                            equipment_item.status = "IDLE"
                        elif reason_item.reason_type == 'scheduled':
                            equipment_item.status = "SCHEDULED"
                    else:
                        equipment_item.status = "BREAKDOWN"
                        new_downtime = MSILDowntime()
                        new_downtime.equipment_id = eqp.id
                        new_downtime.start_time = prev_minute.strftime("%Y-%m-%d %H:%M:%S")
                        # downtime reason need to be picked from table or else 1
                        #downtime reason : no part producde and reason_type_breakdown for shop_id if doesnt exist then 1
                        new_downtime.reason_id = downtime_reason.id if downtime_reason else 1
                        new_downtime.shift = cur_shift
                        new_downtime.shop_id = shop
                        if production_item:
                            if production_item.part_1:
                                part_item = self.session.query(MSILPart).filter(
                                    MSILPart.material_code == production_item.part_1).first()
                                new_downtime.material_code = production_item.part_1
                                new_downtime.part_2_material_code = production_item.part_2
                                new_downtime.model_id = part_item.model_id
                        self.add(new_downtime)
                    self.session.merge(equipment_item)
                self.commit()
            # return cur_minute
        return 'Updated'
    
    def get_top5_breakdown_reasons(self,shop_id,start_time,machine_name):
        cur_datetime = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        print(cur_datetime)
        with self.session:
            query =  self.session.query(
                MSILDowntimeReasons.reason,
                func.sum(
                    case(
                        (
                            self.model_type.end_time.is_(None),
                            (func.extract('epoch', cur_datetime) - func.extract('epoch', self.model_type.start_time)) / 60.0,
                        ),
                        else_=self.model_type.duration
                    ).label('total_duration')
                )
            ) \
            .join(MSILDowntimeReasons, MSILDowntimeReasons.id == self.model_type.reason_id) \
            .group_by(MSILDowntimeReasons.reason) \
            .filter(
                self.model_type.shop_id == shop_id,
                self.model_type.start_time >= start_time
            )

            query = query.join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id)

            if (machine_name):
                query = query.filter(MSILEquipment.name.in_(machine_name))
            return query.order_by(func.sum(
                    case(
                        (
                            self.model_type.end_time.is_(None),
                            (func.extract('epoch', cur_datetime) - func.extract('epoch', self.model_type.start_time)) / 60.0,
                        ),
                        else_=self.model_type.duration
                    )
                ).desc()
            ) \
            .limit(5) \
            .all()
        
    def get_all_downtimes_with_null_end_time(self,shift_start=None,shift_end=None):
        filters = []
        if shift_start is not None and shift_end is not None:
            filters.append(self.model_type.start_time >= shift_start)
            filters.append(self.model_type.start_time < shift_end)
        with self.session:
            return self.session.query(self.model_type) \
                .join(MSILEquipment,self.model_type.equipment_id == MSILEquipment.id)\
                .filter(MSILEquipment.is_deleted.isnot(True))\
                .filter(*filters)\
                .filter(self.model_type.end_time.is_(None)) \
                .all()
                
    def update_unfinished_downtimes(self, downtime_id, end_time):
        # Fetch the specific downtime entry
        downtime_entry = self.session.query(MSILDowntime).filter_by(id=downtime_id).first()
        
        if downtime_entry:
            print("Downtime entry found, updating end_time.")
            downtime_entry.end_time = end_time
            downtime_entry.duration = (int((end_time - downtime_entry.start_time).total_seconds())/60)
            # self.session.merge(downtime_entry)
            self.session.commit()
            self.session.flush()
            
            
            # # Flush and commit the session
            # self.session.flush()  # Stages the changes to be committed
            # self.session.commit()  # Commits the transaction to the database
            print("Update committed successfully.")
        else:
            print("Error: Downtime entry not found.")

    def bulk_insert_downtimes(self,downtimes_arr):
        self.bulk_insert(downtimes_arr)



