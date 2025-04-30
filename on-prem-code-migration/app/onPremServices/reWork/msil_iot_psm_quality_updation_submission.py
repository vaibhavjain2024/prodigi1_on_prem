from fastapi import HTTPException

from os import getenv
from modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from IAM.authorization.psm_shop_authorizer import shop_auth
# from IAM.exceptions.forbidden_exception import ForbiddenException
# from IAM.authorization.base import authorize

from modules.IAM.role import get_role

# from modules.PSM.services.msil_quality_punching_service import MSILQualityPunchingService
from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
# from modules.PSM.services.msil_quality_punching_service import MSILQualityPunchingService
from modules.PSM.services.msil_quality_updation_service import MSILQualityUpdationService


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
    

def handler(punching_id):

    PSM_CONNECTION_STRING = getenv('PSM_CONNECTION_STRING')
    # PLATFORM_CONNECTION_STRING = getenv('PLATFORM_CONNECTION_STRING')

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    # rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_model_repository = MSILModelRepository(session)
    quality_updation_repo = MSILQualityUpdationRepository(session)
    quality_updation_service = MSILQualityUpdationService(quality_updation_repo, msil_equipment_repository, msil_part_repository, msil_model_repository)

    tenant = "MSIL"
    username = "MSIL"

    # role = get_role(username,rbac_session)

    return submit_quality_punching(
        service=quality_updation_service, 
        username=username, 
        # role=role,
        punching_id=punching_id,
    )


    
# @authorize(shop_auth)
def submit_quality_punching(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of alarm/notifications
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILQualityUpdationService =kwargs["service"]
        punching_id = kwargs["punching_id"]
        username = kwargs["username"]

        service.submit_punching(punching_id, username)
        return {"message": "Quality punching record updated successfully"}
        # return {
        #         "statusCode": 200,
        #         "body": json.dumps({"message": "Quality punching record updated successfully", "data": response})
        # }
    except Exception as e:
        logger.error("Failed to Add Quality punching record", exc_info=True)
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
#     role = get_role(username,rbac_session)

#     try:
#         if request_method == "POST":
#             return submit_quality_punching(service=quality_updation_service,
#                                            username=username,
#                                            shop_id=shop_id,
#                                            punching_id=punching_id,
#                                            role = role
#                               )
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")

