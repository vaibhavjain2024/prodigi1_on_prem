from ..rbac.role import Role
from ..rbac.enums import *

def provision_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.PROVISIONING,Actions.PROVISION)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def provision_history_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.PROVISIONING,Actions.GETALL)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs