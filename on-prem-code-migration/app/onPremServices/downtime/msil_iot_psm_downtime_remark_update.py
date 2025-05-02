from modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
import datetime

# from json_utils import default_format_for_json
# from modules.IAM.exceptions.forbidden_exception import ForbiddenException
from modules.IAM.authorization.psm_shop_authorizer import shop_auth
from modules.IAM.authorization.base import authorize
from modules.IAM.role import get_role

from modules.PSM.session_helper import get_session_helper, SessionHelper
from modules.PSM.repositories.msil_part_repository import MSILPartRepository
from modules.PSM.repositories.msil_model_repository import MSILModelRepository
from modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from modules.PSM.services.msil_downtime_service import MSILDowntimeService

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
def get_downtime_remark_status(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of alarm/notifications
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILDowntimeService =kwargs["service"]
        # query_params = kwargs["query_params"]
        
        id = kwargs.get("id")
        # reason = query_params.get("reason")
        remarks = kwargs.get("remarks")
        comment = kwargs.get("comment")
        user = kwargs["username"]
        shop = kwargs.get("shop_id")

        return service.update_remark_by_downtime_id(id,
                               remarks,
                               comment,
                               user,
                               shop
                               )
        # return {
        #         "statusCode": 200,
        #         "body": json.dumps({"message": "Downtime remark updated successfully", "data": response})
        # }

    except Exception as e:
        logger.error("Failed to get downtime remark update", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id, id, remarks, comment, request):
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
    msil_model_repository = MSILModelRepository(session)
    msil_reason_repository = MSILDowntimeReasonRepository(session)
    msil_remark_repository = MSILDowntimeRemarkRepository(session)
    msil_downtime_repository = MSILDowntimeRepository(session)
    msil_shift_repository = MSILShiftRepository(rbac_session)

    msil_downtime_service = MSILDowntimeService(msil_downtime_repository, msil_remark_repository, 
                                        msil_reason_repository,
                                        msil_equipment_repository,
                                        msil_part_repository,
                                        msil_model_repository,
                                        msil_shift_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    # username = query_params.get("username")
    # print(username)
    # date = query_params.get("date",None)

    return get_downtime_remark_status(service=msil_downtime_service,
                                      id=id,
                                      remarks=remarks,
                                      comment=comment,
                                      username=username,
                                      shop_id=shop_id, 
                                      role=role
                                    )
    