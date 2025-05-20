from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from datetime import datetime
from app.modules.common.logger_common import get_logger

# from metrics_logger import log_metrics_to_cloudwatch
# from json_utils import default_format_for_json
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_download_authorizer import psm_download
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_telemetry_repository import MSILTelemetryRepository
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from app.modules.PSM.services.msil_telemetry_service import MSILTelemetryService

# import boto3
# import os
# import csv
# import uuid
# from pandas import ExcelWriter
logger = get_logger()

# s3_client = s3 = boto3.client('s3')
# temp_file_path = "/tmp/latest_production_report.xlsx"
# bucket_name = os.environ.get("PSM_REPORT_S3_BUKCET_NAME")
# folder = "production_reports/"
    
# def upload_to_s3():
#     report_name = "Production_report_" + str(uuid.uuid4()) + ".xlsx"
#     s3_client.upload_file(Filename=temp_file_path, Bucket=bucket_name, Key=folder+report_name)
#     return report_name

def handler(shop_id, start_date, end_date, request, **query_params):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    report_production_repository = MSILTelemetryRepository(session)
    msil_shift_repository = MSILShiftRepository(session)
    report_production_service = MSILTelemetryService(report_production_repository,msil_shift_repository)

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_reports_production(
        service=report_production_service, 
        query_params=query_params,
        username=username, 
        role=role,
        shop_id=shop_id,
        start_date=start_date,
        end_date = end_date
    )

@authorize(psm_download)
def get_reports_production(**kwargs):
    """Get reports 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILTelemetryService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        username = kwargs["username"]
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

        return service.get_production_report_excel(
            shop_id,
            start_date,
            end_date,
            model_list=model_list,
            machine_list=machine_list,
            part_name_list=part_name_list,
            shift=shift
        )

        # if os.path.exists(temp_file_path):
        #     os.remove(temp_file_path)
        
        # xlwriter = ExcelWriter(temp_file_path, engine='xlsxwriter') 


        # response = service.get_production_report_excel(shop_id=shop_id,start_date=start_date,
        #                                             end_date=end_date,
        #                                 model_list=model_list,
        #                                 machine_list=machine_list,
        #                                 part_list=part_name_list,
        #                                 shift=shift,
        #                                 writer=xlwriter
        #                                 )
        # xlwriter.close()
        # report_name = upload_to_s3()

        # report_url = s3_client.generate_presigned_url(
        #         ClientMethod='get_object', 
        #         Params={'Bucket': bucket_name, 'Key': folder+report_name},
        #         ExpiresIn=3600)
                
        # return aws_helper.lambda_response(200, msg = "Success", data = { "report_url" : report_url })

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
    
#     report_production_repository = MSILTelemetryRepository(session)
#     msil_shift_repository = MSILShiftRepository(rbac_session)
#     report_production_service = MSILTelemetryService(report_production_repository,msil_shift_repository)
    
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
#             return get_reports_production(service=report_production_service,
#                                            query_params=query_params, \
#                                             username=username, 
#                                             role=role,
#                                             shop_id=shop_id)
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")