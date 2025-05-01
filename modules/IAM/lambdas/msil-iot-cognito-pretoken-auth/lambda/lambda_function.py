import json
import boto3
import aws_helper
import os
from IAM.session_helper import get_session_helper
from IAM.repositories.user_repository import UserRepository
from IAM.services.user_service import UserService
import time


def create_user(user_name,role,tenant,ts,user_service):
    user_service.create_user({
            "federation_identifier":user_name,
            "roles":role,
            "tenant":tenant,
            "last_loggedin": ts
        })
    return aws_helper.lambda_response(status_code = 200, data={},msg="Success")
        
def get_user(username,user_service):
    user_details = user_service.get_user_by_federation_identifier(username)
    return user_details
    
def update_last_logged_in(username,ts,user_service):
    user = {"federation_identifier": username,
        "last_loggedin": ts}
    response = user_service.update_user_lastlogged_in(user)
    
def lambda_handler(event, context):

    print(event)
    
    #create guest role of msil tenant with permission only to view platform (no admin or usecase access)
    #create user if it doesnt exist with guest role
    #get last logged in at data from user
    #update last logged in at data in user table
    #return last logged in at as attribute (claims to add or override)
    #get tenant and role from user table and return those as claims
    
    connection_string_env_variable = "CONNECTION_STRING"
    env = "production"
    session_helper = get_session_helper(env, connection_string_env_variable)
    session = session_helper.get_session()
    user_repository = UserRepository(session)
    user_service = UserService(user_repository)
    
    user_name = event['userName']
    ts = time.time()
    ts = str(ts)
    ts = ts.split('.')[0]
    
    tenant = event["request"].get("userAttributes",{}).get("custom:tenant",None)
    role = event["request"].get("userAttributes",{}).get("custom:role", None)
    
    user = get_user(user_name,user_service)
    last_loggedin = None
    if(user == None):
        role = ["Guest"]
        tenant = "MSIL"
        res = create_user(user_name,role,tenant,ts,user_service)
        last_loggedin = None
        
    if(user != None):
        last_loggedin = user["last_loggedin"]
        tenant = user["tenant"]
        role = user["roles"] 
        update_last_logged_in(user_name,ts,user_service)
        
   
    if event["response"]["claimsOverrideDetails"] == None:
        event["response"]["claimsOverrideDetails"] = {
            "claimsToAddOrOverride" : {}
        }
    
    
    if tenant != None:
        event["response"]["claimsOverrideDetails"]["claimsToAddOrOverride"]["custom:tenant"] = str(tenant)
    
    if role != None:
        event["response"]["claimsOverrideDetails"]["claimsToAddOrOverride"]["custom:role"] = str(role)
        
    event["response"]["claimsOverrideDetails"]["claimsToAddOrOverride"]["custom:lastloggedin"] = str(last_loggedin)

    print(event)
    return event
