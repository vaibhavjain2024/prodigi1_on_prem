import json
import boto3
import aws_helper
import os
from IAM.session_helper import get_session_helper
from IAM.authorization.admin_authorizer import admin
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
#from IAM.role import  *
from IAM.repositories.user_repository import UserRepository
from IAM.services.user_service import UserService
from IAM.role import  get_role
#from sqlalchemy.pool import NullPool




client = boto3.client(
        'cognito-idp'
    )
user_pool_id = os.environ.get("USER_POOL_ID",None)

# get users dict
def get_user_dict(username,user_attributes,user_service):
    user_attributes_dict  = {user_attributes[i]["Name"]: user_attributes[i] for i in range(0, len(user_attributes))}
    user_details = user_service.get_user_by_federation_identifier(username)
    user = {}
    if(user_details!=None):
        user = {
            "first_name":user_attributes_dict.get("given_name",""),
            "last_name":user_attributes_dict.get("family_name",""),
            "username":username,
            "cognito_role":user_attributes_dict.get("custom:role",{}).get("Value","Admin"),
            "tenant":user_attributes_dict.get("custom:tenant",{}).get("Value","MSIL"),
            "email":user_attributes_dict.get("email",{}).get("Value",""),
            "roles":user_details.get("roles",[]),
            "role_permissions":user_details.get("role_permissions",[])
        }

    return user

@authorize(admin)
def get_all_users(**kwargs):
    client = kwargs["client"]   
    user_pool_id = kwargs["user_pool_id"]
    tenant = kwargs["tenant"]
    user_service = kwargs["user_service"]
    response = client.list_users(
        UserPoolId=user_pool_id,
        Limit = 60
    )
    users = response["Users"]
    users_list = []
    for user in users:
        user_dict = get_user_dict(user["Username"],user["Attributes"],user_service)
        if(user_dict.get("tenant",None)==tenant):
            users_list.append(get_user_dict(user["Username"],user["Attributes"],user_service))
        
    return users_list
    

def get_user(client,user_pool_id,username,user_service):
    response = response = client.admin_get_user(
        UserPoolId=user_pool_id,
        Username=username
    )
    
    return get_user_dict(response["Username"],response["UserAttributes"],user_service)
    

def lambda_handler(event, context):
    print(event)
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
    
    user_repository = UserRepository(session)
    user_service = UserService(user_repository)
    
    # return user_service.get_user_by_federation_identifier("msil-iot_maruti\iot_developer2")
    if(user_pool_id==None):
        return aws_helper.lambda_response(status_code = 400, data={},msg="user pool id not found")
        
    path_params = event.get("pathParameters",{})
    if path_params == None:
        path_params = {}

    tenant = event.get('requestContext',{}) \
                          .get('authorizer',{}) \
                          .get('claims',{}) \
                          .get('custom:tenant',"MSIL")
    role =  event.get('requestContext',{}) \
                          .get('authorizer',{}) \
                          .get('claims',{}) \
                          .get('custom:role',"Admin")
    user = event.get('requestContext',{}) \
                          .get('authorizer',{}) \
                          .get('claims',{}) \
                          .get('cognito:username',"dilpreet")
  
    username = path_params.get("username",None)
    try:
        if(username==None):
            response = get_all_users(role=get_role(user,session),client=client,user_pool_id=user_pool_id,tenant=tenant,user_service=user_service)
        else :
            print(username)
            response = get_user(client,user_pool_id,username,user_service)
            
            
        return aws_helper.lambda_response(status_code = 200, data={"response" : response},msg="Success")

    except Exception as e:
        raise e
        return aws_helper.lambda_response(status_code = 400, data={},msg="Unauthorized access")
        
