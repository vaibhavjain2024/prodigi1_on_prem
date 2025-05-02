from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from modules.common.logger_common import get_logger


# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from IAM.exceptions.forbidden_exception import ForbiddenException
from modules.IAM.authorization.psm_shop_authorizer import shop_auth
from modules.IAM.authorization.base import authorize
from modules.IAM.role import get_role

from modules.PSM.repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
# from modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from modules.PSM.repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
from modules.PSM.services.msil_quality_punching_service import MSILQualityPunchingService

logger = get_logger()

def handler(punching_id, request):
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_model_repository = MSILModelRepository(session)
    msil_updation_repository = MSILQualityUpdationRepository(session)
    msil_quality_punching_repository = MSILQualityPunchingRepository(session)

    msil_quality_punching_service = MSILQualityPunchingService(
        msil_quality_punching_repository,
        msil_equipment_repository,
        msil_part_repository,
        msil_model_repository,
        msil_updation_repository
    )

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_quality_records(
        service=msil_quality_punching_service, 
        username=username, 
        role=role,
        punching_id=punching_id
    )

@authorize(shop_auth)
def get_quality_records(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        # error_message = "Something went wrong"
        service : MSILQualityPunchingService  = kwargs["service"]  
        # query_params = kwargs["query_params"]
        # username = kwargs["username"]
        # shop_id = kwargs["shop_id"]
        punching_id = kwargs["punching_id"]

        return service.get_quality_punching(punching_id) 
                
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }
    except Exception as e:
        logger.error("Failed to get downtime report", exc_info=True)
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
#     msil_updation_repository = MSILQualityUpdationRepository(session)
#     msil_quality_punching_repository = MSILQualityPunchingRepository(session)

#     msil_quality_punching_service = MSILQualityPunchingService(msil_quality_punching_repository,
#                                         msil_equipment_repository,
#                                         msil_part_repository,
#                                         msil_model_repository,
#                                         msil_updation_repository)
    
#     tenant = event.get('requestContext',{}) \
#                           .get('authorizer',{}) \
#                           .get('claims',{}) \
#                           .get('custom:tenant',"MSIL")
    
#     username = event.get('requestContext',{}) \
#                           .get('authorizer',{}) \
#                           .get('claims',{}) \
#                           .get('cognito:username',"MSIL")
    
#     request_method =  event.get("httpMethod","GET")
    
#     shop_id = query_params.get("shop_id","3")
#     role = get_role(username,rbac_session)
#     print("role, Username, tennant, shop_id : ",role, username, tenant, shop_id)
#     try:
#         if request_method == "GET":
#             return get_quality_records(service=msil_quality_punching_service, 
#                                        query_params=query_params, \
#                                         username=username, 
#                                         role=role,
#                                         shop_id=shop_id)
#     except Exception as e:
#         print(f"Unexpected {e=}, {type(e)=}")
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")