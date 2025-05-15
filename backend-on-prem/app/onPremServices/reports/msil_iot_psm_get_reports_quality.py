from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from datetime import datetime
from app.modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_shop_authorizer import shop_auth
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
# from app.modules.PSM.repositories.msil_part_repository import MSILPartRepository
# from app.modules.PSM.repositories.msil_model_repository import MSILModelRepository
# from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
# from app.modules.PSM.repositories.models.msil_quality_punching import MSILQualityPunching
# from app.modules.PSM.repositories.msil_quality_updation_repository import MSILQualityUpdationRepository
# from app.modules.PSM.repositories.msil_quality_punching_repository import MSILQualityPunchingRepository
# from app.modules.PSM.services.msil_quality_punching_service import MSILQualityPunchingService
from app.modules.PSM.repositories.msil_report_quality_repository import MSILReportQualityRepository
from app.modules.PSM.services.msil_report_quality_service import MSILReportQualityService

# import boto3
# import os
# import csv

# import uuid
logger = get_logger()


def handler(shop_id, start_date, end_date, request, **query_params):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    report_quality_repository = MSILReportQualityRepository(session)
    report_quality_service = MSILReportQualityService(report_quality_repository)

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username, rbac_session)

    return get_reports_quality(
        service=report_quality_service, 
        query_params=query_params,
        username=username, 
        role=role,
        shop_id=shop_id,
        start_date=start_date,
        end_date = end_date
    )


@authorize(shop_auth)
def get_reports_quality(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILReportQualityService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        start_date = datetime.strptime(kwargs["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(kwargs["end_date"], "%Y-%m-%d").date()

        model_list = query_params.get("model_list", None)
        if model_list:
            model_list = model_list.split(";")
        machine_list = query_params.get("machine_list", None)
        if machine_list:
            machine_list = machine_list.split(";")
        part_name_list = query_params.get("part_name_list", None)
        if part_name_list:
            part_name_list = part_name_list.split(";")
        shift = query_params.get("shift", None)
        if shift:
            shift = shift.split(";")

        return service.get_machine_quality_data(
            shop_id,
            start_date,
            end_date,
            model_list=model_list,
            machine_list=machine_list,
            part_name_list=part_name_list,
            shift=shift
        )

        # response = service.get_machine_quality_data(shop_id,start_date=start_date,
        #                                             end_date=end_date,
        #                                 model_list=model_list,
        #                                 machine_list=machine_list,
        #                                 part_name_list=part_name_list,
        #                                 shift=shift
        #                                 )
     
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(response,
        #     default=default_format_for_json)
        # }
    except Exception as e:
        logger.error("Failed to get downtime report", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e)
            }
        )

















# @log_metrics_to_cloudwatch
# def lambda_handler(event, context):
#     """Lambda handler to get the latest dimensions trends.
#     """    

#     PSM_CONNECTION_STRING = "PSM_CONNECTION_STRING"
#     PLATFORM_CONNECTION_STRING = "PLATFORM_CONNECTION_STRING"

#     session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
#     session = session_helper.get_session()

#     rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
#     rbac_session = rbac_session_helper.get_session()
    
#     query_params = event.get("queryStringParameters", {})
    
#     logger.info(f"Query Params :: {query_params}")
    
#     report_quality_repository = MSILReportQualityRepository(session)
#     report_quality_service = MSILReportQualityService(report_quality_repository)
    
#     tenant = event.get('requestContext',{}) \
#                           .get('authorizer',{}) \
#                           .get('claims',{}) \
#                           .get('custom:tenant',"MSIL")
    
#     username = event.get('requestContext',{}) \
#                           .get('authorizer',{}) \
#                           .get('claims',{}) \
#                           .get('cognito:username',"MSIL")
    
#     request_method =  event.get("httpMethod","GET")
    
#     shop_id = query_params.get("shop_id","3")
#     role = get_role(username,rbac_session)
#     try:
#         if request_method == "GET":
#             return get_reports_quality(service=report_quality_service, 
#                                        query_params=query_params, \
#                                        username=username, 
#                                        role=role,
#                                        shop_id=shop_id)
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")