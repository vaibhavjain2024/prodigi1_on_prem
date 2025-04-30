from ..rbac.role import Role
from ..rbac.enums import *
from ..exceptions.forbidden_exception import ForbiddenException

def pqc_download(**kwargs):
    role = kwargs["role"]
    shop_id = kwargs["shop_id"]
    scope = {Scopes.ALLOWED_SHOP_IDS:shop_id} 
    permissions = role.check_permission(Resources.PQC_DOWNLOAD,Actions.DOWNLOAD,scope)
    if permissions is False :
        raise ForbiddenException("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

