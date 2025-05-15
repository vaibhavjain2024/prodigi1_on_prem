from .request_handler import RequestHandler
#from validation.base import json_validate
import json 
from IAM.authorization.admin_authorizer import admin
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
from IAM.role import  get_role

#schemas = {}
#with open("schemas/schema.json") as json_file:
#    schemas = json.load(json_file)
        
class PutHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "PUT"
        super().__init__(service, self.request_action, url_path)
    
    
    @authorize(admin)
    def update_role(self,**kwargs):
        body = kwargs["body"]
        return self.service.update_role(body,body["name"],body["tenant"])
        
    
    #@json_validate(json_schema=schemas.get("put_schema",{}))
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        """     
        user = kwargs["identifier"]
        session = kwargs["session"]
        if(self.update_role(
                        body = body,
                        role= get_role(user,session),
                    ) is not None
            ):
            return 200, self.update_role(
                        body = body,
                        role= get_role(user,session),
                    )
        else :
               return  500, "Could not update role"
        
        #except :
        #    return 403, "Unauthorized Access"