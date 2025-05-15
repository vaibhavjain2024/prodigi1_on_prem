from ..rbac.role import Role
from ..rbac.enums import *

def admin(**kwargs):
    role = kwargs["role"]
    permissions = role.check_permission(Resources.ADMIN,Actions.ADMIN)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

