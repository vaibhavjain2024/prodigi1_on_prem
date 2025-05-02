from modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# import json
# import sys
# import datetime
# from json_utils import default_format_for_json
# from modules.IAM.authorization.psm_shop_authorizer import shop_auth
# from modules.IAM.exceptions.forbidden_exception import ForbiddenException
# from modules.IAM.authorization.base import authorize
# from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_recipe_repository import MSILRecipeRepository
from modules.PSM.services.msil_recipe_service import MSILRecipeService

logger = get_logger()
    
# @authorize(shop_auth)
def input_material_update(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Input material with the same production_id, batch_id, and part_name already exists."
        service : MSILRecipeService  = kwargs["service"]  
        # query_params = kwargs["query_params"]
        # username = kwargs["username"]
        body = kwargs["body"]
        # input_materials_list = kwargs["input_materials_list"]
        # shop_id = query_params.get("shop_id")

       

        return service.add_input_materials(body["input_materials_list"])
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

def handler(shop_id, **body):
    """Lambda handler to get the latest dimensions trends.
    """ 
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    # rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session() 
    
    msil_recipe_repository = MSILRecipeRepository(session)

    msil_recipe_service = MSILRecipeService(msil_recipe_repository)
    
    tenant = "MSIL"
    username = "MSIL"

    # role = get_role(username,rbac_session)

    return input_material_update(service=msil_recipe_service, 
                                 body=body,
                                #  username=username,
                                #  role=role, 
                                 shop_id=shop_id
                                 )