import json
import boto3
import aws_helper
import os
from IAM.session_helper import get_session_helper
from IAM.authorization.admin_authorizer import admin
from IAM.rbac.enums import *
from IAM.authorization.base import authorize
from IAM.role import get_role
from IAM.repositories.user_repository import UserRepository
from IAM.services.user_service import UserService
import re


user_pool_id = os.environ.get("USER_POOL_ID",None)

client = boto3.client(
    'cognito-idp'
)



@authorize(admin)
def update_user(**kwargs):
    user_pool_id = kwargs["user_pool_id"]
    client = kwargs["client"]
    user_service = kwargs["user_service"]
    if(user_pool_id==None):
        return aws_helper.lambda_response(status_code = 400, data={},msg="user pool id not found")
    username = kwargs["username"]
    body = kwargs["body"]
    # response = client.admin_update_user_attributes(
    #         UserPoolId=kwargs["user_pool_id"],
    #         Username=username,
    #         UserAttributes=[
    #             {
    #                 'Name': 'given_name',
    #                 'Value': body["first_name"]
    #             },
    #             {
    #                 'Name': 'family_name',
    #                 'Value': body["last_name"]
    #             },
    #             {
    #                 'Name': 'email',
    #                 'Value': body["email"]
    #             },
    #             { 
    #                 'Name': 'custom:role',
    #                 'Value': body["cognito_role"]
    #             },
    #             {
    #                 'Name': 'custom:tenant',
    #                 'Value': body["tenant"]
    #             }
    #         ]
    #     )

    
    # if(response['ResponseMetadata']['HTTPStatusCode']==200):

    user_service.update_user({
        "federation_identifier":body["username"],
        "roles":body.get("roles",[]),
        "tenant":body["tenant"]
    }) 
    return aws_helper.lambda_response(status_code = 200, data={},msg="Success")
    # else :
    #     return aws_helper.lambda_response(status_code = response['ResponseMetadata']['HTTPStatusCode'], data={},msg="Error Occured in updating role")


def validate_user_values(first_name,last_name,email,username,cognito_role,tenant,roles):
    res = False
    if((len(first_name) > 50) or (len(last_name) > 50) or (len(username) > 50) or (len(cognito_role) > 50)or (len(tenant) > 50) or (len(email) > 50)):
        return False
    for role in roles:
        if(re.match("^[A-Za-z0-9 _-]*$", role) != None):
            res = True
        else:
            return False
    if((re.match("^[A-Za-z0-9_-]*$", first_name) != None) and (re.match("^[A-Za-z0-9._-]*$", last_name) != None) and
            (re.match("^[A-Za-z0-9._-]*$", username) != None) and (re.match("^[A-Za-z0-9._-]*$", cognito_role) != None)
            and (re.match("^[A-Za-z0-9._-]*$", tenant) != None) and (re.match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", email) != None) and res):
        res = True
    else:
        return False
    return res    
    
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
    
    user_repository = UserRepository(session)
    user_service = UserService(user_repository)
    body = json.loads(event.get("body","{}"))   
    
    #tenant = event.get('requestContext',{}) \
    #                      .get('authorizer',{}) \
    #                      .get('claims',{}) \
    #                      .get('custom:tenant',"Nagarro")
    
    #role =  event.get('requestContext',{}) \
    #                      .get('authorizer',{}) \
    #                      .get('claims',{}) \
    #                      .get('custom:role',"Admin")
            
    #body["tenant"]=tenant
    identifier = event['requestContext'].get('authorizer',{}).get('claims',{}).get('cognito:username',"dilpreet")
    
    first_name = body.get("first_name","")
    last_name = body.get("last_name","")
    email = body.get("email","")
    username = body.get("username","")
    cognito_role = body.get("cognito_role","")
    tenant = body.get("tenant","")
    roles = body.get("roles",[])
    
    try :
        username = event.get("pathParameters",{}).get("username",None)
        if username == None:
            return aws_helper.lambda_response(status_code = 400, data={},msg="No username provided")
        if(body.get("cognito_role",None)==None):
            return aws_helper.lambda_response(status_code = 400, data={},msg="No role provided")
            
        # res = validate_user_values(first_name,last_name,email,username,cognito_role,tenant,roles)
        res = True
        if res:
            return update_user(
                username = username,
                body = body,
                client = client, 
                user_pool_id = user_pool_id,
                user_service = user_service,
                role = get_role(identifier,session)
            )
        else:
            return aws_helper.lambda_response(status_code = 400, data={},msg="Invalid Input")
    except:
         return aws_helper.lambda_response(status_code = 403, data={},msg="Unauthorized access")
        
