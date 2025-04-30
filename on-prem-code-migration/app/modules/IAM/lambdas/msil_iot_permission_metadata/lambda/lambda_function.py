import boto3
import aws_helper
import os
from IAM.session_helper import get_session_helper
from IAM.repositories.permission_metadata import PermissionMetadataRepository
from IAM.services.permission_metadata import PermissionMetadataService
from IAM.authorization.base import authorize
from IAM.role import get_role
from IAM.authorization.admin_authorizer import admin


@authorize(admin)
def get_all_permission_metadata(**kwargs):
    tenant = kwargs["tenant"]
    permission_metadata_service = kwargs["permission_metadata_service"]   
    return permission_metadata_service.get_all_permission_metadata()
    

def lambda_handler(event, context):
    stage_variables = event.get("stageVariables",{})
    env = None
    if(stage_variables != None):
        env = stage_variables["lambdaAlias"]
    connection_string_env_variable = "CONNECTION_STRING"
    if(env == "development"):
        connection_string_env_variable = "CONNECTION_STRING_DEVELOPMENT"
    elif(env == "QA"):
        connection_string_env_variable = "CONNECTION_STRING_QA"
    elif(env == "staging"):
        connection_string_env_variable = "CONNECTION_STRING_STAGING"
    
    session_helper = get_session_helper(env, connection_string_env_variable)
    session = session_helper.get_session()
    
    permission_metadata_repository = PermissionMetadataRepository(session)
    permission_metadata_service = PermissionMetadataService(permission_metadata_repository)
    
    
    tenant = event.get('requestContext',{}) \
                          .get('authorizer',{}) \
                          .get('claims',{}) \
                          .get('custom:tenant',"MSIL")
                          
    user =event.get('requestContext',{}) \
                          .get('authorizer',{}) \
                          .get('claims',{}) \
                          .get('cognito:username',"dilpreet")
                          
    try:
        response = get_all_permission_metadata(role= get_role(user,session),tenant=tenant,permission_metadata_service=permission_metadata_service)
                
        return aws_helper.lambda_response(status_code = 200, data={"response" : response},msg="Success")
    
    except:
        return aws_helper.lambda_response(status_code = 400, data={},msg="Unauthorized access")
        
