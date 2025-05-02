from IAM.session_helper import get_session_helper
from IAM.repositories.permissions_repository import PermissionsRepository
from IAM.services.permissions_service import  PermissionsService

import json


def setup(env, connection_string_env_variable):
    #this function is to setup dependencies

    #setup db connections here

    #setup repositories here
    session_helper = get_session_helper(env, connection_string_env_variable)
    session = session_helper.get_session()

    permissions_repository = PermissionsRepository(session)
    
    #setup services here 
    permissions_service = PermissionsService(permissions_repository)
    



    #setup object returns the dependencies
    setup = {
      
        "repository" : permissions_repository,
        "service" : permissions_service,
        "session": session
        
    }

    return setup
