import uuid
from ..repositories.models.permission_metadata import PermissionMetadata
from ..repositories.permission_metadata import PermissionMetadataRepository
from ..rbac.enums import  *
import json


class PermissionMetadataService():
    def __init__(self, repository : PermissionMetadataRepository):
        self.repository = repository

    def get_all_permission_metadata(self, include_all_fields = False ):
        permission_model_list = self.repository.get_all()
        permissions_list =[]
        for permission_model in permission_model_list :
            if include_all_fields:
                permissions_list.append(self.transform_from_model_with_all_fileld(permission_model))
            else:
                permissions_list.append(self.transform_from_model(permission_model))
                
        return permissions_list
    
    def get_all_permission_metadata_dict(self):
        permission_model_list = self.repository.get_all()
        permission_model_dict = {each_model.display_name: {"resource" : each_model.resource, 
                                                       "action" : each_model.action, "scope":each_model.scope, 
                                                       "action_type": each_model.action_type   
                                                         } for each_model in permission_model_list}
        return permission_model_dict
    
    def transform_from_model(self, model):
        return{
            "id":str(model.id),
            "resource" : model.resource,
            "action" : model.action,
            "scope":model.scope,
        }
    
    def transform_from_model_with_all_fileld(self, model):
        return{
            "id":str(model.id),
            "resource" : model.resource,
            "action" : model.action,
            "scope":model.scope,
            "action_type": model.action_type,
            "display_name": model.display_name,
            "module_id": model.module_id
        }
    
    def get_permission_meta_by_module_ids(self, module_ids):
        '''
        Gettling the permissions metadata by module_ids
        '''
        permission_model_list =  self.repository.get_permission_meta_by_module_ids(module_ids)
        permissions_list = []
        for permission_model in permission_model_list :
            permissions_list.append(self.transform_from_model_with_all_fileld(permission_model))
        return permissions_list
    
    def get_all_permission_metadata_v2(self, get_map_of_resource_name_and_detail = False):
        permission_model_list = self.repository.get_all_permission_metadata()
        permissions_list = []

        if get_map_of_resource_name_and_detail:
            name_to_detail_map = {}
            for model in permission_model_list:
                name_to_detail_map[model.resource] = self.transform_from_model_with_all_fileld(model)
            return name_to_detail_map

        for model in permission_model_list:
            permissions_list.append(self.transform_from_model_with_all_fileld(model))
        return permissions_list

