from IAM.session_helper import get_session_helper
from IAM.repositories.role_repository import RoleRepository
from IAM.services.role_service import RoleService
import json


def setup(env, connection_string_env_variable):
    #this function is to setup dependencies

    #setup db connections here
    session_helper = get_session_helper(env, connection_string_env_variable)
    session = session_helper.get_session()


    #setup repositories here
    role_repository = RoleRepository(session)
    
    #setup services here 
    role_service = RoleService(role_repository)
    



    #setup object returns the dependencies
    setup = {
      
        "repository" : role_repository,
        "service" : role_service,
        "session": session
    }

    return setup
