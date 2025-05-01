import uuid
from ..repositories.models.permission_metadata import PermissionMetadata
from ..repositories.permission_metadata import PermissionMetadataRepository
from ..rbac.enums import  *
import json


class PermissionMetadataService():
    def __init__(self, repository : PermissionMetadataRepository):
        self.repository = repository

    def get_all_permission_metadata(self):
        permission_model_list = self.repository.get_all()
        permissions_list =[]
        for permission_model in permission_model_list :
            permissions_list.append(self.transform_from_model(permission_model))
        return permissions_list
    
    def transform_from_model(self, model):
        return{
            "id":str(model.id),
            "resource" : model.resource,
            "action" : model.action,
            "scope":model.scope,      
        }

