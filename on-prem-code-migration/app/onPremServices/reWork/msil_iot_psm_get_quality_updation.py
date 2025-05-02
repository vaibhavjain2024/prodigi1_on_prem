from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from modules.IAM.exceptions.forbidden_exception import ForbiddenException
from modules.IAM.authorization.psm_shop_authorizer import shop_auth
from modules.IAM.authorization.base import authorize
from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.models.msil_quality_updation import MSILQualityUpdation
from modules.PSM.repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
from modules.PSM.services.msil_quality_updation_service import MSILQualityUpdationService

# from functools import wraps
logger = get_logger()

# def conditional_authorize(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         role = kwargs.get('role')
#         if role:
#             return authorize(shop_auth)(func)(*args, **kwargs)
#         return func(*args, **kwargs)
#     return wrapper

def handler(shop_id, request, **query_params):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()
    
    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_model_repository = MSILModelRepository(session)
    msil_quality_updation_repository = MSILQualityUpdationRepository(session)

    msil_quality_updation_service = MSILQualityUpdationService(
        msil_quality_updation_repository,
        msil_equipment_repository,
        msil_part_repository,
        msil_model_repository
    )

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_plans(
        service=msil_quality_updation_service, 
        query_params=query_params,
        username=username, 
        role=role,
        shop_id=shop_id
    )


def get_plans(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILQualityUpdationService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        page_no = int(query_params["page_no"])
        page_size = int(query_params["page_size"])
        model_list = query_params.get("model_list", None)
        if model_list:
            model_list = model_list.split(";")
        machine_list = query_params.get("machine_list", None)
        if machine_list:
            machine_list = machine_list.split(";")
        part_name_list = query_params.get("part_name_list", None)
        if part_name_list:
            part_name_list = part_name_list.split(";")
        batch = query_params.get("batch", None)

        start_time = query_params.get("start_time", None)
        end_time = query_params.get("end_time", None)
        shift = query_params.get("shift", None)
        if shift:
            shift = shift.split(";")
        status = query_params.get("status", None)
        
        return service.get_quality_updation(
            shop_id, 
            model_list=model_list,
            machine_list=machine_list,
            part_name_list=part_name_list,
            start_time=start_time,
            end_time=end_time,
            batch=batch,
            shift=shift,
            status=status,
            page_no=page_no,
            page_size=page_size
        )
        
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }
    except Exception as e:
        logger.error("Failed to get plans", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e)
            }
        )



































# # @log_metrics_to_cloudwatch
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
#     msil_quality_updation_repository = MSILQualityUpdationRepository(session)

#     msil_quality_updation_service = MSILQualityUpdationService(msil_quality_updation_repository,
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
#             return get_plans(service=msil_quality_updation_service,
#                               query_params=query_params, \
#                               username=username, 
#                               role=role,
#                               shop_id=shop_id)
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")