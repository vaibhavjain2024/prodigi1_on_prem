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
from modules.PSM.services.msil_recipe_service import MSILRecipeService
from modules.PSM.repositories.msil_production_repository import MSILProductionRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.services.msil_production_service import MSILProductionService

logger = get_logger()
    
# @authorize(shop_auth)
def update_variant(**kwargs):
    """Update variant 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILProductionService  = kwargs["service"]  
        body = kwargs["body"]
        production_id = body["production_id"]
        previous_material_code = body["prev_material_code"]
        material_code = body["material_code"]
        part = body["part"]
        shop_id = body["shop_id"]

        return service.change_variant(production_id, material_code, previous_material_code, part, shop_id)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to update production variant", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(**body):
    """Lambda handler to get the latest dimensions trends.
    """    
    PSM_CONNECTION_STRING = getenv('PSM_CONNECTION_STRING')
    PLATFORM_CONNECTION_STRING = getenv('PLATFORM_CONNECTION_STRING')

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session() 
    
    msil_production_repository = MSILProductionRepository(session)
    msil_shift_repository = MSILShiftRepository(rbac_session)
    msil_production_service = MSILProductionService(msil_production_repository,msil_shift_repository)
    
    tenant = "MSIL"
    username = "MSIL"

    # role = get_role(username,rbac_session)

    # body = json.loads(event.get('body'))
    shop_id = body['shop_id']

    return update_variant(service=msil_production_service, 
                          body=body, 
                        #  role=role, 
                        #  username=username,
                          shop_id=shop_id,
                         )