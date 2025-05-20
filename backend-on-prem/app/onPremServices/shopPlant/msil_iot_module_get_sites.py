from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PLATFORM_CONNECTION_STRING


from app.modules.SM.session_helper import SessionHelper
from app.modules.SM.repository.shop_repository import ShopRepository
from app.modules.SM.services.shop_service import ShopService

def get_all_sites_by_module(**kwargs):
    shop_service = kwargs["shop_service"]
    # query_params = kwargs["query_params"]
    module_name = kwargs.get("module_name","Process Quality and Capability")

    return shop_service.get_all_sites_from_module(module_name)
    

def handler(module_name, request):
    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  

    # session_helper = get_session_helper(env, connection_string_env_variable)
    # rds_session = session_helper.get_session()
    shop_repository = ShopRepository(rbac_session)
    shop_service = ShopService(shop_repository)

    tenant = request.state.tenant
    user = request.state.username

    return get_all_sites_by_module(module_name = module_name,
                                    shop_service=shop_service)
   