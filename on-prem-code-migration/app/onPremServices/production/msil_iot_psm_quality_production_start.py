from modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# import json
# import sys
# import datetime
# import logging
# from json_utils import default_format_for_json
from modules.IAM.authorization.psm_shop_authorizer import shop_auth
from modules.IAM.authorization.base import authorize
from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_production_repository import MSILProductionRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.services.msil_production_service import MSILProductionService

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
    
@authorize(shop_auth)
def start_production(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of alarm/notifications
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILProductionService =kwargs["service"]
        production_id = kwargs["production_id"]
        # username = kwargs["username"]
        body = kwargs["body"]

        return service.start_production(production_id, body["input_materials"],
                                        body["output_parts"],
                                        body["work_order_number_1"],
                                        body.get("work_order_number_2",None))
        # return {
        #         "statusCode": 200,
        #         "body": json.dumps({"message": "Production started!", "data": response})
        # }

    except Exception as e:
        logger.error("Failed to quality production start", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id, production_id, request, **body):
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

    # production_id = query_params.get("production_id", None)

    # body = json.loads(event.get('body'))

    return start_production(service=msil_production_service,
                            username=username,
                            role=role,
                            production_id=production_id, 
                            shop_id=shop_id,
                            body=body
                            )