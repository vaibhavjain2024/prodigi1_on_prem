from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

import pytz
import datetime
from app.modules.PSM.session_helper import get_session_helper, SessionHelper

# import os
# import boto3
# from app.modules.PSM.repositories.msil_plan_file_status_repository import MSILPlanFileStatusRepository
# from app.modules.PSM.services.msil_plan_file_status_service import MSILPlanFileStatusService
# from app.modules.PSM.repositories.models.msil_plan_file_status import MSILPlanFileStatus, PlanFileStatusEnum
# from app.modules.PSM.repositories.msil_alert_repository import MSILAlertRepository
# from app.modules.PSM.repositories.models.msil_alert_notification import AlertNotification
# from app.modules.IAM.authorization.psm_admin_authorizer import admin
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

logger = get_logger()

ist_tz = pytz.timezone('Asia/Kolkata')

# s3_client = s3 = boto3.client('s3')
# bucket_name = os.environ.get("PSM_PLAN_S3_BUCKET_NAME")

def handler(shop_id, shop_name, request):
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

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  

    # msil_planfilestatus_repository = MSILPlanFileStatusRepository(session)
    # msil_alert_repository = MSILAlertRepository(session)
        
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    # query_params = event.get("queryStringParameters", {})
    # shop_id = query_params.get("shop_id")
    # shop_name = query_params.get("shop_name")
    # if None in (shop_id, shop_name) or shop_name == '' or shop_id == '':
    #     return aws_helper.lambda_response(status_code = 400, data={},msg="Error, shop_id/shop_name is not provided.")

    try:
        shop_auth(role=role, shop_id=shop_id)
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
        file_name = f"{shop_name}_{current_ist_time}.xlsx"

        
        date_val = datetime.datetime.now(ist_tz).date()
        # success_filter = {'status':PlanFileStatusEnum.SUCCESS, 'plan_for_date':str(date_val), 'shop_id':shop_id}
        # success_details = msil_planfilestatus_repository.filter_by(**success_filter)
        # if success_details is not None:
        #     notification_obj = AlertNotification()
        #     notification_obj.notification = "Plan already exists for today"
        #     notification_obj.notification_metadata = None
        #     notification_obj.alert_type = "Plan Upload Error"
        #     notification_obj.created_at = datetime.datetime.now(ist_tz).replace(tzinfo=None)
        #     notification_obj.shop_id = shop_id
        #     msil_alert_repository.add(notification_obj)
        #     return aws_helper.lambda_response(400, msg = f"Plan already exists for today", data = {})
    
        print(username)
        print(shop_id)
        # report_url = s3_client.generate_presigned_url(
        #     ClientMethod='put_object', 
        #     Params={'Bucket': bucket_name, 'Key': file_name, 'Metadata' : {'created_by': username, 'shop_id': shop_id}},
        #     ExpiresIn=3600)
            
        # return aws_helper.lambda_response(200, msg = "Success", data = { "plan_url" : report_url})
    except Exception as e:
        logger.error("Failed get signed url for upload plan file", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )



