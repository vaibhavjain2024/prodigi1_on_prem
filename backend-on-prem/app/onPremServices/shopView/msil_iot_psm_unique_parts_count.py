from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from app.modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from IAM.exceptions.forbidden_exception import ForbiddenException

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_plan_repository import MSILPlanRepository
from app.modules.PSM.services.dashboard_service import MSILDashboardService
from app.modules.PSM.repositories.msil_telemetry_repository import MSILTelemetryRepository
from app.modules.PSM.repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
from app.modules.PSM.repositories.msil_production_repository import MSILProductionRepository


from datetime import datetime
logger = get_logger()


def handler(shop_id, request):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()
    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    # rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_telemetry_repo = MSILTelemetryRepository(session)
    quality_punching_repo = MSILQualityPunchingRepository(session)
    msil_plan_repository = MSILPlanRepository(session)
    msil_production_repository = MSILProductionRepository(session)
    dashboard_service = MSILDashboardService(msil_plan_repository,msil_telemetry_repo,quality_punching_repo,msil_production_repository)

    production_date_str = datetime.now().strftime('%Y-%m-%d')
    return get_palnned_progress_completed_parts_metrics(dashboard_service, shop_id, production_date_str)


def get_palnned_progress_completed_parts_metrics(dashboard_service, shop_id, production_date_str) -> dict:
    """Validate Batch

    This function updates batches without an 'end_time' for unclosed batches created in the last shift and restart batches for new shift.
    """

    try:
        return dashboard_service.get_palnned_progress_completed_parts_metrics(shop_id,production_date_str)
        # response =  dashboard_service.get_palnned_progress_completed_parts_metrics(shop_id,production_date_str)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }
    except Exception as e:
        logger.error("Batch validation failed", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e)
            }
        )






















# @log_metrics_to_cloudwatch
# def lambda_handler(event, context):
    
#     logger.info("Lambda function triggered.")

#     PSM_CONNECTION_STRING = "PSM_CONNECTION_STRING"
#     PLATFORM_CONNECTION_STRING = "PLATFORM_CONNECTION_STRING"

#     session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
#     session = session_helper.get_session()

#     rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
#     rbac_session = rbac_session_helper.get_session()

#     msil_telemetry_repo = MSILTelemetryRepository(session)
#     quality_punching_repo = MSILQualityPunchingRepository(session)
#     msil_plan_repository = MSILPlanRepository(session)
#     msil_production_repository = MSILProductionRepository(session)
#     dashboard_service = MSILDashboardService(msil_plan_repository,msil_telemetry_repo,quality_punching_repo,msil_production_repository)
#     query_params = event.get("queryStringParameters", {})
    
#     logger.info(f"Query Params :: {query_params}")
#     shop_id = query_params.get("shop_id","3")
#     try:
#         production_date_str = datetime.now().strftime('%Y-%m-%d')
#         return get_palnned_progress_completed_parts_metrics(dashboard_service,shop_id,production_date_str)
#     except ForbiddenException as exception:
#         logger.error(exception)
#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)

#     logger.info("Lambda function execution completed.")