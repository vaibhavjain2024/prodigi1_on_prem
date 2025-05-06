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
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.services.msil_equipment_service import MSILEquipmentService
logger = get_logger()


def handler(shop_id, request, **query_params):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_shift_repository = MSILShiftRepository(rbac_session)

    msil_equipment_service = MSILEquipmentService(msil_equipment_repository,msil_shift_repository)

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return shop_view_graph(
        service=msil_equipment_service, 
        query_params=query_params,
        username=username, 
        role=role,
        shop_id=shop_id
    )


def shop_view_graph(**kwargs):
    """Get downtime 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILEquipmentService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        view = query_params.get("view", 'CURRENT')
        machine_name = query_params.get("machine_name", None)

        return service.shop_view_graph(
            shop_id,
            machine_name=machine_name,
            view=view
        )

        # response = service.shop_view_graph(shop_id, 
        #                              machine_name=machine_name,
        #                              view=view)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to get machine view graph", exc_info=True)
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
    
#     msil_equipment_repository = MSILEquipmentRepository(session)
#     msil_shift_repository = MSILShiftRepository(rbac_session)

#     msil_equipment_service = MSILEquipmentService(msil_equipment_repository,msil_shift_repository)
    
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
#             return shop_view_graph(service=msil_equipment_service,
#                                     query_params=query_params, \
#                                     username=username, 
#                                     role=role,
#                                     shop_id=shop_id)
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")