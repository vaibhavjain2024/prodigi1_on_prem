from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# import json
# import sys
# import datetime
# from json_utils import default_format_for_json
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_production_repository import MSILProductionRepository
from app.modules.PSM.services.msil_production_service import MSILProductionService
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository

logger = get_logger()

@authorize(shop_auth)
def get_production(**kwargs):
    """Get production 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILProductionService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        equipment_id = query_params["equipment_id"]

        return service.get_production_by_equipment_id(equipment_id)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to get production", exc_info=True)
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
    msil_production_service = MSILProductionService(msil_production_repository,
                                                    msil_shift_repository)
    
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_production(service=msil_production_service, 
                          query_params=query_params, 
                          username=username, 
                          role=role,
                          shop_id=shop_id
                         )
    