# services/dashboard_service.py
from ..repositories.msil_plan_repository import MSILPlanRepository
from ..repositories.msil_telemetry_repository import MSILTelemetryRepository
from ..repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
from ..repositories.msil_production_repository import MSILProductionRepository
from datetime import datetime, timedelta
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')


class MSILDashboardService:
    def __init__(self, plan_repository: MSILPlanRepository, telemetry_service: MSILTelemetryRepository,
                 punching_repository:MSILQualityPunchingRepository, production_repository: MSILProductionRepository):
        self.plan_repository = plan_repository
        self.telemetry_service = telemetry_service
        self.punching_repository = punching_repository
        self.production_repository = production_repository

    def get_palnned_progress_completed_parts_metrics(self,shop_id,production_date_str):
        unique_planned_parts_count = self.plan_repository.get_unique_planned_parts_count(production_date_str,shop_id)
        today_date = datetime.strptime(production_date_str, '%Y-%m-%d')


        start_time = today_date + timedelta(hours=6, minutes=30)
        end_time = today_date + timedelta(days=1, hours=6, minutes=29, seconds=59)

        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        print(start_time_str,end_time_str)
        unique_completed_parts_count = self.punching_repository.get_unique_parts_completed_count(start_time_str,end_time_str,shop_id)
        unique_running_parts_counts = self.production_repository.get_current_parts_in_production(shop_id,production_date_str)
        total_running_parts_count = unique_running_parts_counts[0] + unique_running_parts_counts[1]
        return {
            "unique_planned_parts_count": unique_planned_parts_count,
            "unique_completed_parts_count" : unique_completed_parts_count,
            "total_running_parts_count": total_running_parts_count
    }

