from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from app.modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

# from app.modules.PSM.repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
# from app.modules.PSM.services.msil_quality_punching_service import MSILQualityPunchingService
from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_part_repository import MSILPartRepository
from app.modules.PSM.repositories.msil_model_repository import MSILModelRepository
from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
# from app.modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
# from app.modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
# from app.modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
# from app.modules.PSM.services.msil_downtime_service import MSILDowntimeService
from app.modules.PSM.repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
# from app.modules.PSM.services.msil_quality_punching_service import MSILQualityPunchingService
from app.modules.PSM.services.msil_quality_updation_service import MSILQualityUpdationService

logger = get_logger()

# def default_format_for_json(obj):
#     """Handler for dict data helps to serialize it to Json.
#     This method is used to cast the dict values to isoformat if the type of value is date/datetime.
#     Args:
#         obj (any): values of dict.
#     Returns:
#         None/datetime: if obj is data/datetime then date/datetime in isoformat otherwise None.
#     """    
#     if isinstance(obj, (datetime.date, datetime.datetime)):
#         return obj.isoformat()

def handler(punching_id, updation_list, request):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_model_repository = MSILModelRepository(session)
    quality_updation_repo = MSILQualityUpdationRepository(session)
    quality_updation_service = MSILQualityUpdationService(quality_updation_repo, msil_equipment_repository, msil_part_repository, msil_model_repository)

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return put_quality_punching_records(
        service=quality_updation_service, 
        username=username, 
        role=role,
        punching_id=punching_id,
        updation_list=updation_list
    )
    
@authorize(shop_auth)
def put_quality_punching_records(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of alarm/notifications
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILQualityUpdationService =kwargs["service"]
        updation_list = kwargs["updation_list"]
        punching_id = kwargs["punching_id"]
        username = kwargs["username"]

        service.update_updation(punching_id, updation_list, username)
        return {"message": "Quality punching record updated successfully"}
        # return {
        #         "statusCode": 200,
        #         "body": json.dumps({"message": "Quality punching record updated successfully", "data": response})
        # }

    except Exception as e:
        logger.error("Failed to update Quality punching record", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e)
            }
        )
























# @log_metrics_to_cloudwatch
# def lambda_handler(event, context):
#     """Lambda handler to get the latest dimensions trends.
#     """    

#     PSM_CONNECTION_STRING = "PSM_CONNECTION_STRING"
#     PLATFORM_CONNECTION_STRING = "PLATFORM_CONNECTION_STRING"

#     session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
#     session = session_helper.get_session()

#     rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
#     rbac_session = rbac_session_helper.get_session()
    
#     query_params = event.get("queryStringParameters", {})
    
#     logger.info(f"Query Params :: {query_params}")
    
#     msil_part_repository = MSILPartRepository(session)
#     msil_equipment_repository = MSILEquipmentRepository(session)
#     msil_model_repository = MSILModelRepository(session)
#     quality_updation_repo = MSILQualityUpdationRepository(session)
#     quality_updation_service = MSILQualityUpdationService(quality_updation_repo, msil_equipment_repository, msil_part_repository, msil_model_repository)
#     tenant = event.get('requestContext',{}) \
#                           .get('authorizer',{}) \
#                           .get('claims',{}) \
#                           .get('custom:tenant',"MSIL")
    
#     username = event.get('requestContext',{}) \
#                           .get('authorizer',{}) \
#                           .get('claims',{}) \
#                           .get('cognito:username',"MSIL")
    
#     request_method =  event.get("httpMethod","PUT")
#     shop_id = query_params.get("shop_id","3")
#     punching_id = query_params.get("punching_id", None)
#     body = json.loads(event.get('body'))
#     role = get_role(username,rbac_session)

#     try:
#         if request_method == "PUT":
#             return put_quality_punching_records(service=quality_updation_service,
#                                                 body=body,
#                                                 username=username,
#                                                 shop_id=shop_id,
#                                                 punching_id=punching_id,
#                                                 role=role
#                               )
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")

