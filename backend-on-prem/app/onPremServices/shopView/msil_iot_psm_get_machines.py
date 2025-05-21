from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from app.modules.PSM.services.msil_equipment_service import MSILEquipmentService
# from app.modules.PSM.repositories.msil_part_repository import MSILPartRepository
# from app.modules.PSM.repositories.msil_model_repository import MSILModelRepository
# from app.modules.PSM.repositories.msil_plan_repository import MSILPlanRepository
# from app.modules.PSM.repositories.msil_variant_repository import MSILVariantRepository
# from app.modules.PSM.repositories.msil_alert_repository import MSILAlertRepository
# from app.modules.PSM.services.msil_plan_service import MSILPlanService
# from app.modules.PSM.repositories.msil_plan_file_status_repository import MSILPlanFileStatusRepository
# from app.modules.PSM.utilities import common_utilities

logger = get_logger()
    
@authorize(shop_auth)
def get_machines(**kwargs):
    """Get machines 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILEquipmentService  = kwargs["service"]  
        shop_id = kwargs["shop_id"]

        return service.get_machines_by_shop(shop_id)
    
    except Exception as e:
        logger.error("Failed to get machine list", exc_info=True)
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
    
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_shift_repository = MSILShiftRepository(session)
    msil_equipment_service = MSILEquipmentService(msil_equipment_repository,msil_shift_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_machines(service=msil_equipment_service,
                        username=username, 
                        role=role,
                        shop_id=shop_id
                        )
