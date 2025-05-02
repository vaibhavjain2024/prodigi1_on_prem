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
        
class PutHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "PUT"
        super().__init__(service, self.request_action, url_path)
    
    def update_permissions(self,**kwargs):
        body = kwargs["body"]
        return self.service.update_permission(body,body["resource"])

    #@json_validate(json_schema=schemas.get("put_schema",{}))
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        """     
        #add validated thing group to the db
        
        try :
            return 200, self.update_permissions(
                body = body,
                #role =  get_role("test2@gmail.com")
            )
        except : 
            return 403, "Unauthorized Access"
            