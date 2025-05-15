from ..rbac.role import Role
from ..rbac.enums import *

def update_signature(**kwargs):
    role = kwargs["role"]
    shop_id = kwargs["scope_level"]
    scope = {Scopes.ALLOWED_SHOP_IDS:shop_id}  
    permissions = role.check_permission(Resources.UPDATE_SIGNATURE,Actions.UPDATE,scope)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

