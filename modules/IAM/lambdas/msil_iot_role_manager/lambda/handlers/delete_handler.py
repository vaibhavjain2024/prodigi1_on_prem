from .request_handler import RequestHandler
#from validation.base import json_validate
import json 
from IAM.authorization.admin_authorizer import admin
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
from IAM.role import  get_role

# schemas = {}
# with open("schemas/schema.json") as json_file:
#     schemas = json.load(json_file)
        

class DeleteHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "DELETE"
        super().__init__(service, self.request_action, url_path)

    @authorize(admin)
    def delete_role(self,**kwargs):
        body = kwargs["body"]
        return self.service.delete_role(body["name"],body["tenant"])
        
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        """    
        path_params = kwargs["path_params"]
        role_name = path_params.get("name", None)
        user = kwargs["identifier"]
        session = kwargs["session"]
        if role_name != None:
            body["name"]=role_name
            
            return 200, self.delete_role(
                    body = body,
                    role= get_role(user,session)
                ) 
            
        else :
            return 500, "No role name passed"