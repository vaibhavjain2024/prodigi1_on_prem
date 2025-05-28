import uuid
from ..repositories.models.role import Role
from ..repositories.role_repository import RoleRepository
from .permissions_service import  PermissionsService
from ..repositories.permissions_repository import PermissionsRepository
from ..rbac.enums import  *


class RoleService():
    def __init__(self, repository : RoleRepository):
        self.repository = repository
        self.permissions_repository = PermissionsRepository(self.repository.session)
        self.permissions_service = PermissionsService(self.permissions_repository)

    def get_role(self,role_id):
        role_model = self.repository.get(role_id)
        if(role_model!=None):
            return self.transform_from_model(role_model)
        else :
            return None

    def get_roles_by_tenant(self,tenant):
        role_list = []
        role_model_list = self.repository.get_roles_by_tenant(tenant)
        for role_model in role_model_list:
            role_list.append(self.transform_from_model(role_model))
        return role_list
        
    def get_role_by_name_and_tenant_name(self,role_name, tenant):
        role_model = self.repository.get_role_by_tenant_and_name(tenant,role_name)
        if(role_model!=None):
            return self.transform_from_model(role_model)
        else :
            return None
    
    def create_role(self,role):
      
        role_model = Role()
        self.transform_from_dict(role_model, role)
        self.repository.add(role_model)
        role["id"] = str(role_model.id)
        for permission in role.get("permissions",[]):
            permission["role_id"]=role["id"]
            self.permissions_service.create_permission(permission)
        return role
    
    def update_role(self,role,role_name,tenant):
    
        role_model = self.repository.get_role_by_tenant_and_name(tenant,role_name)
        if(role_model!=None):
            self.transform_from_dict(role_model, role)
            self.repository.update(role_model.id,role)
            return self.transform_from_model(role_model)
        else:
            return None

    def delete_role(self,role_name,tenant):
        role_model = self.repository.get_role_by_tenant_and_name(tenant,role_name)
        permission_model = self.permissions_service.get_permissions_by_role_id(role_model.id)
        for i in range(0,len(permission_model)):
            self.permissions_service.delete_permission(permission_model[i]["resource"])
        if(role_model!=None):
            id = role_model.id
            self.repository.remove(id)
            return {
                "id":str(id)
            }
        else : 
            return None

    def get_permissionsList(self,role_id,parent_role):
        permissionList=[]
        permissionList +=self.permissions_service.get_permissions_by_role_id(role_id)
        while(parent_role!=None):
            permissionList+=(self.permissions_service.get_permissions_by_role_id(parent_role))
            parent_role_model = self.repository.get(parent_role)
            parent_role = parent_role_model.parent_role_id
        return permissionList

    def transform_from_model(self, model):
        return{
            "id": model.id,
            "name":model.name,
            "permissions" : self.get_permissionsList(model.id,model.parent_role_id),
            "parent_role_id" : model.parent_role_id,
            "tenant":model.tenant,
            "is_admin":model.is_admin,
            "is_super_admin":model.is_super_admin
        }

    def transform_from_dict(self, model, model_dict):
        if model_dict.get("name", None) != None:
            model.name = model_dict["name"]
        if model_dict.get("tenant", None) != None:
            model.tenant = model_dict["tenant"]
        if model_dict.get("parent_role_id", None) != None:
            model.parent_role_id = (model_dict["parent_role_id"])
        if model_dict.get("is_admin", None) != None:
            model.is_admin = (model_dict["is_admin"])
        if model_dict.get("is_super_admin", None) != None:
            model.is_super_admin = (model_dict["is_super_admin"])

    def transform_from_model_v2(self, model, permissions):
        return{
            "id": model.id,
            "name":model.name,
            "permissions" : permissions,
            "parent_role_id" : model.parent_role_id,
            "tenant":model.tenant,
            "is_admin":model.is_admin,
            "is_super_admin":model.is_super_admin
        }
    
    def get_role_and_permission_details(self, role_ids):
        role_details_list = self.repository.get_role_by_ids(role_ids)
        role_wise_permissions = self.permissions_service.aggregate_permission_details_by_role_ids(role_ids)
        role_id_to_details_map = {}
        for role_model in role_details_list:
            role_id_to_details_map[role_model.id] = self.transform_from_model_v2(
                role_model, role_wise_permissions[role_model.id]
            )
        return role_id_to_details_map


    