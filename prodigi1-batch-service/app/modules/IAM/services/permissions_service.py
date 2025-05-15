import uuid
from ..repositories.models.permission import Permission
from ..repositories.permissions_repository import PermissionsRepository
from ..rbac.enums import  *
import json


class PermissionsService():
    def __init__(self, repository : PermissionsRepository):
        self.repository = repository

    def get_all_permissions(self):
        permission_model_list = self.repository.get_all()
        permissions_list =[]
        for permission_model in permission_model_list :
            permissions_list.append(self.transform_from_model(permission_model))
        return permissions_list
    
    def get_permission(self,resource_name):
        
        permission_model = self.repository.get_permissions_by_resource_name(resource_name)
        return self.transform_from_model(permission_model)
        # permissions_list =[]
        # for permission_model in permission_model_list :
        #     permissions_list.append(self.transform_from_model(permission_model))
        # return permission_model

    def get_permissions_by_role_id(self,role_id):
        
        permission_model_list = self.repository.get_permissions_by_role_id(role_id)
        permissions_list =[]
        for permission_model in permission_model_list :
            permissions_list.append(self.transform_from_model(permission_model))
        return permissions_list
    
    def create_permission(self,permission):
        permission_model = Permission()
        self.transform_from_dict(permission_model, permission)
        self.repository.add(permission_model)
        permission["id"] = str(permission_model.id)
        return permission
    
    def update_permission(self,permission,resource_name):
    
        permission_model = self.repository.get_permissions_by_resource_name(resource_name)
       
        if(permission_model!=None):
            self.transform_from_dict(permission_model, permission)
            self.repository.update(permission_model.id,permission)
            return self.transform_from_model(permission_model)
        else:
            return None

    def delete_permission(self,resource_name):
        permission_model = self.repository.get_permissions_by_resource_name(resource_name)
        if(permission_model!=None):
            id = permission_model.id
            self.repository.remove(id)
            return {
                "id":str(id)
            }
        else : 
            return None

   

    def transform_from_model(self, model):
        return{
            "id":str(model.id),
            "resource" : model.resource,
            "action" : model.action,
            "action_type":model.action_type,
            "scope":model.scope,
            "role_id":model.role_id
            
        }

    def transform_from_dict(self, model, model_dict):
        if model_dict.get("resource", None) != None:
            model.resource = model_dict["resource"]
        if model_dict.get("action", None) != None:
            model.action = model_dict["action"]
        if model_dict.get("role_id", None) != None:
            model.role_id = model_dict["role_id"]
        if model_dict.get("scope", None) != None:
            model.scope = model_dict["scope"]
        if model_dict.get("action_type", None) != None:
            model.action_type = model_dict["action_type"]
