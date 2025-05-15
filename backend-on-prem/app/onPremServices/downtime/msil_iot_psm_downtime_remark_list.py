from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# import json
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from app.modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from app.modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from app.modules.PSM.services.msil_downtime_service import MSILDowntimeService
from app.modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from app.modules.PSM.services.msil_downtime_remark_service import MSILDowntimeRemarkService

logger = get_logger()

@authorize(shop_auth)
def get_downtime_remark_list(**kwargs):
    """Get downtime 

    Returns:
        dict: API response with statusCode and required response of lines
    """
    error_message = "Something went wrong"
    try :
        service : MSILDowntimeRemarkService  = kwargs["service"]
        shop_id = kwargs["shop_id"]  # Get the shop_id from query parameters

        return service.get_remarks_with_reasons_id(shop_id = shop_id)

    except Exception as e:
        logger.error("Failed to get downtime remark list", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )


def handler(shop_id, request):
    """Lambda handler to get the latest dimensions trends.
    """ 
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  
    
    msil_reason_repository = MSILDowntimeReasonRepository(session)
    msil_remark_repository = MSILDowntimeRemarkRepository(session)
    msil_downtime_repository = MSILDowntimeRepository(session)

    msil_downtime_remark_service = MSILDowntimeRemarkService(msil_remark_repository, 
                                        msil_reason_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_downtime_remark_list(service=msil_downtime_remark_service,
                                    username=username,
                                    role=role,
                                    shop_id=shop_id
                                    )