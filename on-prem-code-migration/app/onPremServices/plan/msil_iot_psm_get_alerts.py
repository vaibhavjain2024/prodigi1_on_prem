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
from modules.PSM.repositories.msil_alert_repository import MSILAlertRepository
from modules.PSM.services.msil_alert_service import MSILAlertService

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
def get_alerts(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of alarm/notifications
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILAlertService = kwargs["service"] 
        shop_id = kwargs["shop_id"]

        return service.get_alert_notifications(shop_id)

        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to get alerts", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id):
    """Lambda handler to get the latest dimensions trends.
    """    
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    # rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  
    
    alert_repository = MSILAlertRepository(session)
    alert_service = MSILAlertService(alert_repository)
    
    tenant = "MSIL"
    username = "MSIL"

    # role = get_role(username,rbac_session)
    return get_alerts(service=alert_service, 
                      shop_id=shop_id, 
                    #   role=role
                      )