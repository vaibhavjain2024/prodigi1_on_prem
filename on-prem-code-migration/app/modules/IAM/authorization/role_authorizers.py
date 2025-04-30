from ..rbac.role import Role
from ..rbac.enums import *
#from services.permission_validator_service import PermissionValidatorService

def assign_role_authorizer(**kwargs):
    role = kwargs["role"]
    if(role.check_admin()):
        return kwargs
    else:
        raise Exception("Unauthorized access")

def create_role_authorizer(**kwargs):
    role = kwargs["role"]
   
    if(role.check_admin()):
        return kwargs
    else:
        raise Exception("Unauthorized access")

def update_role_authorizer(**kwargs):
    role = kwargs["role"]
    if(role.check_admin()):
        return kwargs
    else:
        raise Exception("Unauthorized access")

def delete_role_authorizer(**kwargs):
    role = kwargs["role"]
    if(role.check_admin()):
        return kwargs
    else:
        raise Exception("Unauthorized access")
