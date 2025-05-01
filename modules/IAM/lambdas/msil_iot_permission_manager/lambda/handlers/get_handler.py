from .request_handler import RequestHandler
from setup import setup
import time
import json 
from IAM.authorization.role_authorizers import *
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
from IAM.role import  get_role


class GetHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "GET"
        super().__init__(service, self.request_action, url_path)
    
    def check_permission(self,username,rds_session):
        role = get_role(username,rds_session)
        print("#########",role.permissions)
        if 'ADMIN' in role.permissions.keys():
            return True
        return False
        
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        """ 
        rds_session = kwargs.get("rds_session")
        res = self.check_permission(body["identifier"],rds_session)
        if res:
            path_params = kwargs["path_params"]
            query_params = kwargs["query_params"]
            resource_name = path_params.get("name", None)
            if resource_name != None:
                return 200, self.service.get_permission(resource_name)
            else:
               
                return 200, self.service.get_all_permissions()
        else:
            return 403, "Unauthorized access"