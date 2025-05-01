from .request_handler import RequestHandler
#from validation.base import json_validate
import json 
from IAM.authorization.admin_authorizer import admin
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
from IAM.role import  get_role
import re



# schemas = {}
# with open("schemas/schema.json") as json_file:
#     schemas = json.load(json_file)
        

class PostHandler(RequestHandler):
    def __init__(self, service,url_path):
        self.request_action = "POST"
        super().__init__(service, self.request_action, url_path)
    
   
        
    @authorize(admin)
    def create_role(self,**kwargs):
        body = kwargs["body"]
        return self.service.create_role(body)
    
    def validate_role_values(self,name,tenant):
        res = False
        if(len(name) < 1):
            return False
        if((len(name) > 50) or (len(tenant) > 50)):
            return False
        if((re.match("^[A-Za-z0-9 :_-]*$", name) != None) and (re.match("^[A-Za-z0-9 _-]*$", tenant) != None)):
            res = True
        else:
            return False
        return res    
        
    # @json_validate(json_schema=schemas.get("post_schema",{}))
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        """  
        name = body.get("name","")
        tenant = body.get("tenant","")
        try :
            user = kwargs["identifier"]
            session = kwargs["session"]
            res = self.validate_role_values(name,tenant)
            if res:
                return 200, self.create_role(
                        body = body,
                        role = get_role(user,session),
                        #role_permissions = body
                    )
            else:
                return 400, "Invalid Input"
        
        except:
            raise
            return 403, "Unauthorized access"
        