from .request_handler import RequestHandler
#from validation.base import json_validate
import json 
from IAM.authorization.role_authorizers import *
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
#from IAM.role import  get_role

# schemas = {}
# with open("schemas/schema.json") as json_file:
#     schemas = json.load(json_file)
        

class DeleteHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "DELETE"
        super().__init__(service, self.request_action, url_path)

    def delete_permission(self,**kwargs):
        body = kwargs["body"]
        return self.service.delete_permission(body["resource"])

    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        """    
        path_params = kwargs["path_params"]
        resource_name = path_params.get("name", None)
        if resource_name != None:
            body["resource"]=resource_name       
            try :
                return 200, self.delete_permission(
                    body = body,
                    #role =  get_role("test2@gmail.com")
                )
            except:
                return 403, "Unauthorized Access"
        else :
            return 500, "No resource name passed"    
            