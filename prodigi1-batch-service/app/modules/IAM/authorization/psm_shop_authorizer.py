from ..rbac.role import Role
from ..rbac.enums import *
from ..exceptions.forbidden_exception import ForbiddenException
def shop_auth(**kwargs):
    role = kwargs["role"]
    shop_id = kwargs.get("shop_id") or kwargs.get("query_params",{}).get("shop_id")
    permissions = role.check_permission(Resources.PSM_SHOP,Actions.ANY, {Scopes.ALLOWED_SHOP_IDS : shop_id})
    if permissions is False :
        raise ForbiddenException("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

