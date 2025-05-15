from ..rbac.role import Role
from ..rbac.enums import *

def connection_history_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.DEVICE_CONNECT,Actions.GETALL)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def connect_authorizer(**kwargs):
    role = kwargs["role"]
    connection_type = kwargs["scope_level"]
    permissions = role.check_permission(Resources.DEVICE_CONNECT,Actions.CONNECT,{Scopes.CONNECTION_TYPE:connection_type})
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs