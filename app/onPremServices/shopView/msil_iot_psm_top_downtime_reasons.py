from fastapi import HTTPException

from os import getenv
from datetime import datetime, timedelta
from modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from IAM.exceptions.forbidden_exception import ForbiddenException


from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.services.msil_downtime_service import MSILDowntimeService


logger = get_logger()

def handler(shop_id, **query_params):
    PSM_CONNECTION_STRING = getenv('PSM_CONNECTION_STRING')
    # PLATFORM_CONNECTION_STRING = environ.get('PLATFORM_CONNECTION_STRING')

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()
    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    msil_downtime_repo = MSILDowntimeRepository(session)
    msil_downtime_reason = MSILDowntimeReasonRepository(session)
    msil_downtime_remark = MSILDowntimeRemarkRepository(session)
    msil_shift_repository = MSILShiftRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_part_repository = MSILPartRepository(session)
    msil_model_repository = MSILModelRepository(session)
    msil_downtime_service = MSILDowntimeService(msil_downtime_repo,  msil_downtime_remark, msil_downtime_reason, msil_equipment_repository, msil_part_repository, msil_model_repository, msil_shift_repository)

    machine_list = query_params.get("machine_list","ALL")
    if machine_list:
        machine_list = machine_list.split(";")

    production_date_str = datetime.now().strftime('%Y-%m-%d')
    today_date = datetime.strptime(production_date_str, '%Y-%m-%d')
    start_time = today_date + timedelta(hours=6, minutes=30)
    return get_top5_breakdown_reasons(msil_downtime_service, shop_id,start_time, machine_list)


def get_top5_breakdown_reasons(downtime_service, shop_id,start_time,machine_list):
    """Validate Batch

    This function updates batches without an 'end_time' for unclosed batches created in the last shift and restart batches for new shift.
    """

    try:
        return downtime_service.get_top5_breakdown_reasons(shop_id, start_time, machine_list)
        # response =  downtime_service.get_top5_breakdown_reasons(shop_id,start_time,machine_list)
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

#     msil_downtime_repo = MSILDowntimeRepository(session)
#     msil_downtime_reason = MSILDowntimeReasonRepository(session)
#     msil_downtime_remark = MSILDowntimeRemarkRepository(session)
#     msil_shift_repository = MSILShiftRepository(session)
#     msil_equipment_repository = MSILEquipmentRepository(session)
#     msil_part_repository = MSILPartRepository(session)
#     msil_model_repository = MSILModelRepository(session)
#     msil_downtime_service = MSILDowntimeService(msil_downtime_repo,  msil_downtime_remark, msil_downtime_reason, msil_equipment_repository, msil_part_repository, msil_model_repository, msil_shift_repository)
#     query_params = event.get("queryStringParameters", {})
    
#     logger.info(f"Query Params :: {query_params}")
#     shop_id = query_params.get("shop_id","3")
#     machine_list = query_params.get("machine_list","ALL")
#     if machine_list:
#             machine_list = machine_list.split(";")
#     try:
#         production_date_str = datetime.now().strftime('%Y-%m-%d')
#         today_date = datetime.strptime(production_date_str, '%Y-%m-%d')
#         start_time = today_date + timedelta(hours=6, minutes=30)
#         return get_top5_breakdown_reasons(msil_downtime_service,shop_id,start_time,machine_list)
#     except ForbiddenException as exception:
#         logger.error(exception)
#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)

#     logger.info("Lambda function execution completed.")