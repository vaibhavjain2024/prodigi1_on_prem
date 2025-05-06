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
from modules.PSM.repositories.msil_production_repository import MSILProductionRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.services.msil_production_service import MSILProductionService

logger = get_logger()
    
@authorize(shop_auth)
def update_production_status(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILProductionService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        production_id = query_params.get("production_id")
        # shop_id = kwargs["shop_id"]

        return service.pause_production_status(production_id)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to production part data", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id, request, **query_params):
    """Lambda handler to get the latest dimensions trends.
    """ 
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session() 
    
    
    msil_production_repository = MSILProductionRepository(session)
    msil_shift_repository = MSILShiftRepository(rbac_session)
    
    msil_production_service = MSILProductionService(msil_production_repository,msil_shift_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)
    # production_id = query_params.get("production_id")

    return update_production_status(service=msil_production_service,
                                    query_params=query_params, 
                                    username=username,
                                    role=role, 
                                    shop_id=shop_id,
                                    )
    