from modules.common.logger_common import get_logger
from fastapi import HTTPException
from os import getenv

# import json
# import sys
# from json_utils import default_format_for_json
# from modules.IAM.authorization.psm_shop_authorizer import shop_auth
# from modules.IAM.exceptions.forbidden_exception import ForbiddenException
# from modules.IAM.authorization.base import authorize
# from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_plan_file_status_repository import MSILPlanFileStatusRepository
from modules.PSM.services.msil_plan_file_status_service import MSILPlanFileStatusService
import datetime
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')
logger = get_logger()

# def default_format_for_json(obj):
#     """Handler for dict data helps to serialize it to Json.

#     This method is used to cast the dict values to isoformat if the type of value is date/datetime.

#     Args:
#         obj (any): values of dict.

#     Returns:
#         None/datetime: if obj is data/datetime then date/datetime in isoformat otherwise None.
#     """    
#     if isinstance(obj, (datetime.date, datetime.datetime)):
#         return obj.isoformat()
    
# @authorize(shop_auth)
def get_status(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of alarm/notifications
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILPlanFileStatusService =kwargs["service"]
        shop_id = kwargs["shop_id"]
        date = datetime.datetime.now(ist_tz).date()

        return service.get_file_status(shop_id, date)

        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to get file status", exc_info=True)
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
    
    status_repository = MSILPlanFileStatusRepository(session)
    status_service = MSILPlanFileStatusService(status_repository)
    
    tenant = "MSIL"
    username = "MSIL"

    # role = get_role(username,rbac_session)
    # date = query_params.get("date",None)

    return get_status(service=status_service, 
                      shop_id=shop_id, 
                    #   date=date, 
                    #   role=role
                      )
    