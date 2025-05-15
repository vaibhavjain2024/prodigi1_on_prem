from ..rbac.role import Role
from ..rbac.enums import *

def device_list_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.DEVICE,Actions.GETALL)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def device_detail_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.DEVICE,Actions.GET)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs
    

def component_deployed_authorizers(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.COMPONENTS,Actions.GETALL)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def component_detail_authorizers(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.COMPONENTS,Actions.GET)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def sensors_list_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.SENSORS,Actions.GETALL)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def sensors_detail_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.SENSORS,Actions.GET)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def sensors_write_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.SENSORS,Actions.CREATE)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def sensors_update_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.SENSORS,Actions.UPDATE)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

def device_logs_authorizer(**kwargs):
    role = kwargs["role"]
    
    permissions = role.check_permission(Resources.LOGS,Actions.GETALL)
    if permissions is False :
        raise Exception("Unauthorized access")
    else :
        kwargs["authorizer:level"]=permissions
    return kwargs

    
