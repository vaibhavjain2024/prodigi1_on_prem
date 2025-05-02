from ..rbac.role import Role
from ..rbac.enums import *
from ..exceptions.forbidden_exception import ForbiddenException

def admin(**kwargs):
    role = kwargs["role"]
    permissions = role.check_permission(Resources.PQC_ADMIN,Actions.ADMIN)
    if permissions is False :
        raise ForbiddenException("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

