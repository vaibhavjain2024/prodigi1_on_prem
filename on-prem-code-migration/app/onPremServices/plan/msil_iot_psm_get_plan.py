from modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# import json
# import sys
# import datetime
# from json_utils import default_format_for_json
# from modules.IAM.exceptions.forbidden_exception import ForbiddenException
from modules.IAM.authorization.psm_shop_authorizer import shop_auth
from modules.IAM.authorization.base import authorize
from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.msil_plan_repository import MSILPlanRepository
from modules.PSM.repositories.msil_variant_repository import MSILVariantRepository
from modules.PSM.repositories.msil_alert_repository import MSILAlertRepository
from modules.PSM.services.msil_plan_service import MSILPlanService
from modules.PSM.repositories.msil_plan_file_status_repository import MSILPlanFileStatusRepository
from functools import wraps

logger = get_logger()

# def conditional_authorize(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         role = kwargs.get('role')
#         if role:
#             return authorize(shop_auth)(func)(*args, **kwargs)
#         return func(*args, **kwargs)
#     return wrapper

    
@authorize(shop_auth)
def get_plans(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILPlanService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]
        page_no = int(kwargs["page_no"])
        page_size = int(kwargs["page_size"])

        model_list = query_params.get("model_list", None)
        if model_list:
            model_list = model_list.split(";")
        machine_list = query_params.get("machine_list", None)
        if machine_list:
            machine_list = machine_list.split(";")
        part_name_list = query_params.get("part_name_list", None)
        if part_name_list:
            part_name_list = part_name_list.split(";")
        pe_code_list = query_params.get("pe_code_list", None)
        if pe_code_list:
            pe_code_list = pe_code_list.split(";")
        production_date_list = query_params.get("production_date_list", None)
        if production_date_list:
            production_date_list = production_date_list.split(";")
        shift = query_params.get("shift", None)
        priority = query_params.get("priority", None)
        status = query_params.get("status", None)
        sort_priority = query_params.get("sort_priority", None)

        return service.get_plans(shop_id, 
                                 model_list=model_list,
                                 machine_list=machine_list,
                                 part_name_list=part_name_list,
                                 pe_code_list=pe_code_list,
                                 production_date_list=production_date_list,
                                 shift=shift,
                                 priority=priority,
                                 sort_priority=sort_priority,
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
        logger.error("Failed to get plan", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id, page_no, page_size, request, **query_params):
    """Lambda handler to get the latest dimensions trends.
    """ 
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  
    
    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_plan_repository = MSILPlanRepository(session)
    msil_alert_repository = MSILAlertRepository(session)
    msil_variant_repository = MSILVariantRepository(session)
    msil_model_repository = MSILModelRepository(session)
    msil_plan_file_status_repository = MSILPlanFileStatusRepository(session)

    msil_plan_service = MSILPlanService(msil_plan_repository, msil_part_repository, 
                                        msil_equipment_repository,
                                        msil_variant_repository,
                                        msil_model_repository,
                                        msil_alert_repository,
                                        msil_plan_file_status_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_plans(service=msil_plan_service, 
                     query_params=query_params, 
                     username=username, 
                     role=role,
                     shop_id=shop_id,
                     page_no=page_no,
                     page_size = page_size
                     )