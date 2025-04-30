from .models.msil_variant import MSILVariant
from .repository import Repository
from .models.msil_plan import MSILPlan, PlanStatusEnum
from .models.msil_part import MSILPart
from .models.msil_model import MSILModel
from .models.msil_batch import MSILBatch
from .models.msil_shift import MSILShift
from .models.msil_production import MSILProduction
from .models.msil_equipment import MSILEquipment
from .models.shop_configuration import ShopConfiguration
from .models.msil_alert_notification import AlertNotification
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import (
    and_,
    desc,
    func,
    case,
    not_    
)
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')


class MSILPlanRepository(Repository):
    """
    MSILPlanRepository to manage MSILPlan data table.
    """

    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILPlan

    def get_work_orders(self, shop_id, parts, production_date):
        with self.session:       
            return self.session.query(self.model_type.work_order_number.label("work_order_number"),
                                       self.model_type.material_code.label("output_part")) \
                                .filter(self.model_type.shop_id == shop_id) \
                                .filter(self.model_type.production_date == production_date) \
                                .filter(self.model_type.material_code.in_(parts)) \
                                .all()
    
    def actual_count_subquery(self):
        with self.session:
            return self.session.query(func.sum(MSILBatch.prod_qty).label("actual_qty"),
                                        MSILBatch.material_code.label("material_code"),
                                        MSILProduction.date.label("production_date"),
                                        MSILProduction.equipment_id.label("equipment_id")) \
                                .join(MSILProduction, MSILProduction.id == MSILBatch.production_id) \
                                .group_by(MSILProduction.date, MSILProduction.equipment_id, MSILBatch.material_code) \
                                .subquery()

    def get_sorted_plans(self, shop_id, machine_list=None,
                            model_list=None, part_name_list=None,
                            sort_priority=None,
                            pe_code_list=None, production_date_list=None, 
                            shift=None, priority=None, 
                            status=None,  limit=10, offset=0):
        """Get sorted plans from db 
        Default sort : By date, priority, status

        Returns:
            model_list: list of models
        """
        with self.session:
            actual_count_subquery = self.actual_count_subquery()
            query = self.session.query(self.model_type,
                                       MSILModel.model_name,
                                       MSILPart.part_name,
                                       MSILPart.pe_code,
                                       MSILEquipment.name,
                                       MSILVariant.common_name,
                                       MSILPart.material_code,
                                       actual_count_subquery.c.actual_qty) \
                .filter(self.model_type.shop_id == shop_id)\
                .filter(not_(and_(self.model_type.planned_quantity == 0,actual_count_subquery.c.actual_qty == 0)))\

            query = query.filter(self.model_type.priority != 0)
            query.filter((not_(and_(self.model_type.planned_quantity == 0,self.model_type.actual_quantity == 0))))

            if (production_date_list):
                query = query.filter(self.model_type.production_date.in_(production_date_list))

            if (shift):
                query = query.filter(self.model_type.shift == shift)

            if (priority):
                query = query.filter(self.model_type.priority == priority)

            if (status):
                query = query.filter(self.model_type.status == status)

            query = query.join(MSILModel, self.model_type.model_id == MSILModel.id)

            if (model_list):
                query = query.filter(MSILModel.model_name.in_(model_list))

            query = query.join(MSILPart, self.model_type.material_code == MSILPart.material_code)

            if (part_name_list):
                query = query.filter(MSILPart.part_name.in_(part_name_list))

            if (pe_code_list):
                query = query.filter(MSILPart.pe_code.in_(pe_code_list))

            query = query.join(MSILEquipment, self.model_type.equipment_id == MSILEquipment.id)

            if (machine_list):
                query = query.filter(MSILEquipment.name.in_(machine_list))

            query = query.join(MSILVariant, self.model_type.variant_id == MSILVariant.id, isouter=True)

            query = query.join(actual_count_subquery,
                               (actual_count_subquery.c.production_date == self.model_type.production_date)
                               & (actual_count_subquery.c.equipment_id == self.model_type.equipment_id)
                               & (actual_count_subquery.c.material_code == self.model_type.material_code), isouter=True)
            
            query = query.filter(not_(and_(MSILPlan.planned_quantity == 0,actual_count_subquery.c.actual_qty == 0)))

            if (sort_priority):
                if (sort_priority == "desc"):
                    return query.order_by(desc(self.model_type.priority)) \
                        .limit(limit) \
                        .offset(offset) \
                        .all()
                else:
                    return query.order_by(self.model_type.priority) \
                        .limit(limit) \
                        .offset(offset) \
                        .all()

            return query.order_by(desc(self.model_type.production_date)) \
                .order_by(self.model_type.status) \
                .order_by(self.model_type.priority) \
                .limit(limit) \
                .offset(offset) \
                .all()

    def update_plan_statuses(self,today):
        try:

            yesterday_date = today - timedelta(days=1)

            # print(yesterday_date)

            plans = (
                self.session.query(MSILPlan)
                .filter(MSILPlan.production_date == yesterday_date)
                .all()
            )
            # print(plans)

            for plan in plans:
                yesterday_batches = (
                    self.session.query(func.sum(MSILBatch.prod_qty))
                    .join(MSILProduction, MSILProduction.id == MSILBatch.production_id) \
                    .filter(MSILBatch.material_code == plan.material_code,
                            MSILProduction.date == yesterday_date).scalar()
                )
                # print(yesterday_batches)
                if yesterday_batches is None:
                    yesterday_batches = 0

                if plan.planned_quantity > yesterday_batches:

                    plan.status = PlanStatusEnum.SHORT_CLOSED
                elif yesterday_batches >= plan.planned_quantity:

                    plan.status = PlanStatusEnum.COMPLETED
                # print(plan.status)
                self.session.commit()

        except Exception as e:

            self.session.rollback()
            raise e

    def get_unique_planned_parts_count(self, production_date, shop_id):
        with self.session:
            grouped_query = self.session.query(self.model_type.equipment_id.label("equipment_id"),
                                               MSILPart.material_code.label("material_code")) \
                .join(MSILPart, self.model_type.material_code == MSILPart.material_code) \
                .filter(self.model_type.shop_id == shop_id) \
                .filter(self.model_type.production_date == production_date) \
                .group_by(self.model_type.equipment_id, MSILPart.material_code)
            unique_planned_parts_count = self.session.query(func.count()).select_from(grouped_query.subquery()).scalar()
            return unique_planned_parts_count


    def get_existing_plan(self, equipment_id, model_id, variant_id, shift,material_code, production_date_arr):
        with self.session:
            filters = []
            filters.append(MSILPlan.variant_id== variant_id)
            filters.append(MSILPlan.equipment_id == equipment_id)
            filters.append(MSILPlan.model_id == model_id)
            filters.append(MSILPlan.production_date.in_(production_date_arr))
            filters.append(MSILPlan.material_code == material_code)
            if shift is not None:
                MSILPlan.shift = str(shift)

            query = self.session.query(MSILPlan.production_date, MSILPlan.id).filter(*filters).all()
            dates = {}
            for each in query:
                date, plan_id = each
                dates[date] = plan_id
            return dates
    
    def get_plan_cache(self,production_date_arr,shop_id):
        filters = []
        filters.append(MSILPlan.production_date >= production_date_arr)
        filters.append(MSILPlan.shop_id == shop_id)
        with self.session:
            query = self.session.query(MSILPlan.id,
                               MSILPlan.variant_id,
                               MSILPlan.equipment_id,
                               MSILPlan.model_id,
                               MSILPlan.material_code,
                               MSILPlan.production_date,
                               MSILPlan.shift)\
                                .filter(*filters)\
                                .order_by(MSILPlan.variant_id,
                                            MSILPlan.equipment_id,
                                            MSILPlan.model_id,
                                            MSILPlan.material_code,
                                            ).filter(*filters).all()
            return query
                
    def insert_plan(self,plan_items_need_to_inserted):
        self.bulk_insert(plan_items_need_to_inserted)

    def get_shift(self, shop_id, time):
        with self.session:
            all_shifts = self.session.query(MSILShift).filter(MSILShift.shop_id == shop_id).all()
            shift = None
            for each_shift in all_shifts:
                if each_shift.shift_start_timing <= time <= each_shift.shift_end_timing:
                    shift = each_shift.shift_name
            return shift

    def update_the_existing_planned_quantity(self,id,pqty, priority):
        with self.session:
            self.session.query(MSILPlan).filter(MSILPlan.id == id).update({MSILPlan.planned_quantity:pqty,MSILPlan.priority:priority, MSILPlan.status: PlanStatusEnum.PLANNED.value})
            self.session.commit()

    def bulk_update_existing_plans(self, updates):
        """Bulk update existing planned quantities and priorities."""
        if not updates:
            return

        with self.session as session:
            for update in updates:
                session.query(MSILPlan).filter(MSILPlan.id == update['id']).update({
                    MSILPlan.planned_quantity: update['planned_quantity'],
                    MSILPlan.priority: update['priority'],
                    MSILPlan.status: PlanStatusEnum.PLANNED.value
                })
            session.commit()

    def get_shop_configuration(self,shop_id):
        with self.session:
            shop_config =self.session.query(ShopConfiguration)\
                .filter(ShopConfiguration.shop_id==shop_id)\
                .first()
            if shop_config == None:
                is_day = True
                is_shift = False
                return is_day,is_shift
            else:
                return shop_config.is_day,shop_config.is_shift

    def get_all_shops(self):
        with self.session:
            return self.session.query(
                ShopConfiguration.id,
                ShopConfiguration.shop_id,
                ShopConfiguration.is_day,
                ShopConfiguration.is_shift,
                ShopConfiguration.shop_timing
            ).all()

    def get_plan_for_default_job(self, shop_id, date):
        with self.session:
            query =(self.session.query(
                MSILPlan.id,
                MSILPlan.model_id,
                MSILPlan.variant_id,
                MSILPlan.production_date,
                MSILPlan.shift,
                MSILPlan.shop_id,
                MSILPlan.actual_quantity,
                MSILPlan.planned_quantity,
                MSILPlan.status
            ).filter(MSILPlan.shop_id == shop_id)
            .filter(MSILPlan.production_date == date)
            .all())

            return query

    def marking_all_the_planned_quantities_as_unplanned(self, shop_id, date):
        with self.session:
            self.session.query(MSILPlan)\
            .filter(MSILPlan.shop_id == shop_id, MSILPlan.production_date == date)\
            .update({
                MSILPlan.planned_quantity:0,
                MSILPlan.status :PlanStatusEnum.UNPLANNED.value
                            })
            self.session.commit()

    def update_the_existing_planned_status(self,id,status):
        with self.session:
            self.session.query(MSILPlan).filter(MSILPlan.id == id).update({MSILPlan.status:status})
            self.session.commit()

    def bulk_update_plan_status(self,updates):
        """Bulk update existing planned quantities and priorities."""
        if not updates:
            return

        with self.session as session:
            for update in updates:
                session.query(MSILPlan).filter(MSILPlan.id == update['id']).update({
                    MSILPlan.status: update['status']
                })
            session.commit()

    def get_plan_datewise(self,shop_id,production_date):
        with self.session:
            actual_count_subquery = self.actual_count_subquery()
            return self.session.query(
                MSILPlan.id,
                actual_count_subquery.c.actual_qty,
                MSILPlan.planned_quantity,
                MSILPlan.status
            ).filter(MSILPlan.shop_id == shop_id)\
            .filter(MSILPlan.production_date == production_date)\
            .join(actual_count_subquery,
            (actual_count_subquery.c.production_date == MSILPlan.production_date)
            & (actual_count_subquery.c.equipment_id == MSILPlan.equipment_id)
            & (actual_count_subquery.c.material_code == MSILPlan.material_code), isouter=True)\
            .all()

    def raise_alert_notification(self,shop_id,errors):
        alert_model = AlertNotification()
        alert_model.created_at = datetime.now(ist_tz).date()
        alert_model.alert_type = "Plan Upload Error"
        alert_model.notification_metadata = {
            'errors' : errors
        }
        alert_model.notification = "Unable to upload the Plan"
        alert_model.shop_id = shop_id
        with self.session:
            self.session.add(alert_model)
            self.session.commit()

    def raise_unplanned_alert_notification(self,
                                           model_name,
                                           variant_name,
                                           part_name,
                                           line_name,
                                           shop_id,
                                           errors=[]):
        alert_model = AlertNotification()
        alert_model.created_at = datetime.now(ist_tz).date()
        alert_model.alert_type = "Unplanned production"
        alert_model.notification_metadata = {
            'errors' : errors
        }
        alert_model.notification = f"{model_name} {variant_name} {part_name} is not planned on {line_name}, but production is on"
        alert_model.shop_id = shop_id
        with self.session:
            self.session.add(alert_model)
            self.session.commit()

