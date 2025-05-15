from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from app.modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_part_repository import MSILPartRepository
from app.modules.PSM.repositories.msil_model_repository import MSILModelRepository
from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
# from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
from app.modules.PSM.repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
from app.modules.PSM.services.msil_quality_updation_service import MSILQualityUpdationService

# from PSM.repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
# from PSM.services.msil_quality_punching_service import MSILQualityPunchingService

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

    msil_quality_updation_service = MSILQualityUpdationService(
        msil_updation_repository,
        msil_equipment_repository,
        msil_part_repository,
        msil_model_repository
    )

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username, rbac_session)

    return get_updation_records(
        service=msil_quality_updation_service, 
        username=username, 
        role=role,
        punching_id=punching_id
    )

@authorize(shop_auth)
def get_updation_records(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILQualityUpdationService  = kwargs["service"]  
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
        logger.error("Failed to get updation records", exc_info=True)
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

#     msil_quality_updation_service = MSILQualityUpdationService(msil_updation_repository,
#                                         msil_equipment_repository,
#                                         msil_part_repository,
#                                         msil_model_repository)
    
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
#     try:
#         if request_method == "GET":
#             return get_updation_records(service=msil_quality_updation_service, 
#                                         query_params=query_params, \
#                                         username=username, 
#                                         role=role,
#                                         shop_id=shop_id)
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")