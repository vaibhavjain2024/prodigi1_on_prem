from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from app.modules.common.logger_common import get_logger

# from json_utils import default_format_for_json
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from app.modules.PSM.services.msil_downtime_service import MSILDowntimeService
from app.modules.PSM.repositories.msil_part_repository import MSILPartRepository
from app.modules.PSM.repositories.msil_model_repository import MSILModelRepository
from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from app.modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from app.modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from app.modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from app.modules.PSM.services.msil_downtime_service import MSILDowntimeService

logger = get_logger()

@authorize(shop_auth)
def get_downtime_filters(**kwargs):
    """Get alarms 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILDowntimeService  = kwargs["service"]  
        # query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        return service.get_downtime_part_filters(shop_id)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }

    except Exception as e:
        logger.error("Failed to get downtime filter", exc_info=True)
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
    
    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_remark_repository = MSILDowntimeRemarkRepository(session)
    msil_reason_repository = MSILDowntimeReasonRepository(session)
    msil_downtime_repository= MSILDowntimeRepository(session)
    msil_model_repository = MSILModelRepository(session)
    msil_shift_repository = MSILShiftRepository(session)

    msil_downtime_service = MSILDowntimeService(msil_downtime_repository, msil_remark_repository, 
                                        msil_reason_repository,
                                        msil_equipment_repository,
                                        msil_part_repository,
                                        msil_model_repository,
                                        msil_shift_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_downtime_filters(service=msil_downtime_service, 
                                        username=username, 
                                        role=role,
                                        shop_id=str(shop_id))