from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

import datetime
from app.modules.PSM.session_helper import get_session_helper, SessionHelper

# import os
import pytz
# import boto3
# from app.modules.IAM.authorization.psm_admin_authorizer import admin
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_download_authorizer import psm_download
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

logger = get_logger()

ist_tz = pytz.timezone('Asia/Kolkata')

# s3_client = s3 = boto3.client('s3')
# bucket_name = os.environ.get("PSM_PLAN_S3_BUCKET_NAME")
# folder = ""

def handler(shop_id, shop_name, date_str=None, request=None):
    """Lambda handler to provide the presigned url to upload the master file to S3.
    """    
    # stage_variables = event.get("stageVariables",{})
    # env = None
    
    # if(stage_variables != None):
    #     env = stage_variables["lambdaAlias"]
    # connection_string_env_variable = "CONNECTION_STRING"
    # rbac_connection_string = "RBAC_CONNECTION_STRING"
    # if(env == "development"):
    #     connection_string_env_variable = "CONNECTION_STRING_DEVELOPMENT"
    #     rbac_connection_string = "RBAC_CONNECTION_STRING_DEVELOPMENT"
    # elif(env == "QA"):
    #     connection_string_env_variable = "CONNECTION_STRING_QA"
    #     rbac_connection_string = "RBAC_CONNECTION_STRING_QA"
    # elif(env == "staging"):
    #     connection_string_env_variable = "CONNECTION_STRING_STAGING"
    #     rbac_connection_string = "RBAC_CONNECTION_STRING_STAGING"


    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    # session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  
        
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)
    print(role)

    # query_params = event.get("queryStringParameters", {})
    # shop_id = query_params.get("shop_id")
    # shop_name = query_params.get("shop_name")
    # date_str = query_params.get("date")
    # if None in (shop_id, shop_name) or shop_name == '' or shop_id == '':
    #     return aws_helper.lambda_response(status_code = 400, data={},msg="Error, shop_id/shop_name is not provided.")

    try:
        psm_download(role=role, shop_id=shop_id)
        # admin(role=role)
    except Exception as e:
        logger.error("Forbidden, shop not accessible", exc_info=True)
        raise HTTPException(
            status_code=403,
            detail={
                "error": str(e)
            }
        )
    
    try:
        current_ist_time = datetime.datetime.now(ist_tz).strftime("%d%m%y")
        if date_str:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            current_ist_time = date_obj.strftime("%d%m%y")

        file_name = f"{shop_name}_{current_ist_time}.xlsx"

        return {
            "statusCode": 200,
            "body": {
                "file_name": file_name,
                "url": f"https://{shop_name}.s3.ap-south-1.amazonaws.com/{file_name}"
            }
        }

        # plan_url = s3_client.generate_presigned_url(
        #     ClientMethod='get_object', 
        #     Params={'Bucket': bucket_name, 'Key': folder+file_name},
        #     ExpiresIn=3600)
            
        # return aws_helper.lambda_response(200, msg = "Success", data = { "plan_url" : plan_url})
    except Exception as e:
        logger.error("Failed get signed url for download plan file", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )


