from modules.common.logger_common import get_logger
from fastapi import HTTPException
from os import getenv

# import json
# import sys
# import datetime
# from json_utils import default_format_for_json
# from modules.IAM.authorization.psm_shop_authorizer import shop_auth
# from modules.IAM.exceptions.forbidden_exception import ForbiddenException
# from modules.IAM.authorization.base import authorize
# from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.services.msil_part_service import MSILPartService

logger = get_logger()
    
# @authorize(shop_auth)
def get_plan_filters(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILPartService  = kwargs["service"]  
        # query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        return service.get_part_filters(shop_id)
    
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }
    
    except Exception as e:
        logger.error("Failed to get plan filters", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id):
    """Lambda handler to get the latest dimensions trends.
    """    
    PSM_CONNECTION_STRING = getenv('PSM_CONNECTION_STRING')
    # PLATFORM_CONNECTION_STRING = getenv('PLATFORM_CONNECTION_STRING')

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    # rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()
    
    part_repository = MSILPartRepository(session)
    part_service = MSILPartService(part_repository)
    
    tenant = "MSIL"
    username = "MSIL"

    # role = get_role(username,rbac_session)

    return get_plan_filters(service=part_service, 
                            # query_params=query_params,
                            # username=username, 
                            shop_id=shop_id, 
                            # role=role
                            )
    