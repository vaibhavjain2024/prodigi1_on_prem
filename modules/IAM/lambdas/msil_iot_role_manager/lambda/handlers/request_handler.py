#from validation.base import json_validate
import json 

        
        
class RequestHandler():
    def __init__(self, service, request_action="GET", url_path="/"):
        self.service = service
        self.request_action = request_action
        self.url_path = url_path

    
    def process(self,**kwargs):
        """Processes the request

        Args:
            body (dict): Request body that is validated by the validation schema
        """      
        #common logic for each handler

        return self.process_request(**kwargs)
    
    
    def process_request(self,body, **kwargs):
        """Process request, to be implemented by the child class

        Args:
            body (dict): Request body 

        Raises:
            Exception: Not implemented exception, child class needs to implement this method
        """        
        raise Exception("Not implemented")

    