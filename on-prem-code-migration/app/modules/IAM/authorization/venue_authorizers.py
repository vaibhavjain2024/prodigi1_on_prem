from ..rbac.role import Role
from ..rbac.enums import *

def venue_list_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission("VENUE",Actions.GETALL)
    kwargs["authorizer:level"]=permissions
    return kwargs

def venue_detail_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission("VENUE",Actions.GET)
    kwargs["authorizer:level"]=permissions
    return kwargs

