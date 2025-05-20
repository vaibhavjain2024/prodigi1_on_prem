from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# import os
# import csv
# import uuid
# import json
# import boto3
# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_download_authorizer import psm_download
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_part_repository import MSILPartRepository
from app.modules.PSM.repositories.msil_model_repository import MSILModelRepository
from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from app.modules.PSM.repositories.msil_downtime_reason_repository import MSILDowntimeReasonRepository
from app.modules.PSM.repositories.msil_downtime_remarks_repository import MSILDowntimeRemarkRepository
from app.modules.PSM.repositories.msil_downtime_repository import MSILDowntimeRepository
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from app.modules.PSM.services.msil_downtime_service import MSILDowntimeService
from functools import wraps

logger = get_logger()

# def conditional_authorize(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         role = kwargs.get('role')
#         if role:
#             return authorize(psm_download)(func)(*args, **kwargs)
#         return func(*args, **kwargs)
#     return wrapper

# s3_client = s3 = boto3.client('s3')
# temp_file_path = "/tmp/latest_report_with_filter.csv"
# bucket_name = os.environ.get("PSM_REPORT_S3_BUKCET_NAME")
# folder = "plan_reports/"
    
# def upload_to_s3():
#     report_name = "Downtime_report_" + str(uuid.uuid4()) + ".csv"
    
#     s3_client.upload_file(Filename=temp_file_path, Bucket=bucket_name, Key=folder+report_name)

#     return report_name

@authorize(psm_download)
def get_plans(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        error_message = "Something went wrong"
        service : MSILDowntimeService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        model_list = query_params.get("model_list", None)
        if model_list:
            model_list = model_list.split(";")
        machine_list = query_params.get("machine_list", None)
        if machine_list:
            machine_list = machine_list.split(";")
        part_name_list = query_params.get("part_name_list", None)
        if part_name_list:
            part_name_list = part_name_list.split(";")
        start_time = query_params.get("start_time", None)
        end_time = query_params.get("end_time", None)
        duration = query_params.get("duration", None)
        if duration == "0-5 mins":
            start=0
            end=5
        elif duration == "5-10 mins":
            start=5
            end=10
        elif duration == "10-30 mins":
            start=10
            end=30
        elif duration == ">30 mins":
            start=30
            end=None
        else:
            start=None
            end=None
        shift = query_params.get("shift", None)
        if shift:
            shift = shift.split(";")
        reason = query_params.get("reason", None)
        if reason:
            reason = reason.split(";")
        remarks = query_params.get("remarks", None)
        if remarks:
            remarks = remarks.split(";")

        return service.get_downtime_report(
            None, 
            shop_id, 
            model_list=model_list,
            machine_list=machine_list,
            part_name_list=part_name_list,
            start_time=start_time,
            end_time=end_time,
            start=start,
            end=end,
            shift=shift,
            reason=reason,
            remarks=remarks
            )

        # if os.path.exists(temp_file_path):
        #     os.remove(temp_file_path)
        
        # with open(temp_file_path, 'w') as csvfile: 
        #     # creating a csv writer object 
        #     csvwriter = csv.writer(csvfile) 

        #     service.get_downtime_report(csvwriter, shop_id, 
        #                                 model_list=model_list,
        #                                 machine_list=machine_list,
        #                                 part_name_list=part_name_list,
        #                                 start_time=start_time,
        #                                 end_time=end_time,
        #                                 start=start,
        #                                 end=end,
        #                                 shift=shift,
        #                                 reason=reason,
        #                                 remarks=remarks)
        # report_name = upload_to_s3()

        # report_url = s3_client.generate_presigned_url(
        #         ClientMethod='get_object', 
        #         Params={'Bucket': bucket_name, 'Key': folder+report_name},
        #         ExpiresIn=3600)
                
        # return aws_helper.lambda_response(200, msg = "Success", data = { "report_url" : report_url })

    except Exception as e:
        logger.error("Failed to get downtime", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e)
            }
        )

def handler(shop_id, request, **query_params):
    """Lambda handler to get the latest dimensions trends.
    """    
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  
    
    msil_part_repository = MSILPartRepository(session)
    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_remark_repository = MSILDowntimeRemarkRepository(session)
    msil_reason_repository = MSILDowntimeReasonRepository(session)
    msil_downtime_repository= MSILDowntimeRepository(session)
    msil_model_repository = MSILModelRepository(session)
    msil_shift_repository = MSILShiftRepository(session)

    msil_downtime_service = MSILDowntimeService(msil_downtime_repository, msil_remark_repository, 
                                        msil_reason_repository,
                                        msil_equipment_repository,
                                        msil_part_repository,
                                        msil_model_repository,
                                        msil_shift_repository)
    
    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_plans(service=msil_downtime_service,
                     query_params=query_params,
                     username=username,
                     role=role, 
                     shop_id=shop_id
                     )
    