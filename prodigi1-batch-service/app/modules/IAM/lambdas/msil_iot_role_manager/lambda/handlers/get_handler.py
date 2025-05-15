from .request_handler import RequestHandler
from setup import setup
import concurrent.futures
#import pymongo
from datetime import datetime
#from bson import ObjectId
from IAM.authorization.base import authorize
from IAM.role import get_role
from IAM.authorization.admin_authorizer import admin
import time


class GetHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "GET"
        super().__init__(service, self.request_action, url_path)
    
    @authorize(admin)
    def get_role(self,**kwargs):
        role_name = kwargs["role_name"]
        tenant = kwargs["tenant"]
        if role_name != None:
            return self.service.get_role_by_name_and_tenant_name(role_name,tenant)
        else:
            return self.service.get_roles_by_tenant(tenant)
        
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body  

        """     
        try:
            user = kwargs["identifier"]
            session = kwargs["session"]
            role_name = kwargs.get("path_params",{}).get("name", None)
            
            print(f"role_name = {role_name}") 
            if role_name == "me":
                role_name = body["role"]
                  
            tenant  = body["tenant"]
            
            return 200, self.get_role(
                    role_name = role_name,
                    role = get_role(user,session),
                    tenant = tenant
                )
        
        except:
            return 403, "Unauthorized access"