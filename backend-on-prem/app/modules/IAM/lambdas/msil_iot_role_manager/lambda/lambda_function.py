from handlers.get_handler import GetHandler
from handlers.post_handler import PostHandler
from handlers.put_handler import PutHandler
from handlers.delete_handler import DeleteHandler
from setup import setup
import aws_helper
import json

def get_handler(http_method, service, url_path):
    if http_method == "GET":
        return GetHandler(service, url_path)

    if http_method == "POST":
        return PostHandler(service, url_path)

    if http_method == "PUT":
        return PutHandler(service, url_path)

    if http_method == "DELETE":
        return DeleteHandler(service, url_path)

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

    dependencies = setup(env, connection_string_env_variable)
    service = dependencies["service"]
    session = dependencies["session"]
    #process event object
    query_params = event.get("queryStringParameters",{})
    path_params = event.get("pathParameters",{})
    if path_params == None:
        path_params = {}
    url_path = event.get("path","")
    http_method = event.get("httpMethod","GET")
    if event.get("body")!=None:
        print(event.get("body","{}"))
        body = json.loads(event.get("body","{}"))
    else:
        body = {}
        
    body["tenant"] = event.get('requestContext',{}) \
                          .get('authorizer',{}) \
                          .get('claims',{}) \
                          .get('custom:tenant',"MSIL")

    #body["role"] =  event.get('requestContext',{}) \
                          #.get('authorizer',{}) \
                          #.get('claims',{}) \
                          #.get('custom:role',"Admin")
    identifier = event['requestContext'].get('authorizer',{}).get('claims',{}).get('cognito:username',"dilpreet")
    handler = get_handler(http_method, service, url_path,)
    status_code, response = handler.process(body=body, query_params=query_params, path_params=path_params,session = session,identifier = identifier)

    
    #TODO : use helper lib for response
    return aws_helper.lambda_response(status_code = status_code, data={"response" : response},msg="Success")


