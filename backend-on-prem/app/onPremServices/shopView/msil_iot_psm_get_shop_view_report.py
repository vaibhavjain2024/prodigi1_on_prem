from fastapi import HTTPException

from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from app.modules.common.logger_common import get_logger

# from app.modules.IAM.exceptions.forbidden_exception import ForbiddenException
from app.modules.IAM.authorization.psm_download_authorizer import psm_download
from app.modules.IAM.authorization.base import authorize
from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.PSM.repositories.msil_equipment_repository import MSILEquipmentRepository
from app.modules.PSM.repositories.msil_shift_repository import MSILShiftRepository
from app.modules.PSM.services.msil_equipment_service import MSILEquipmentService


# from functools import wraps
# import csv
logger = get_logger()

def handler(shop_id, request, **query_params):

    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()
    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()
    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()

    msil_equipment_repository = MSILEquipmentRepository(session)
    msil_shift_repository = MSILShiftRepository(rbac_session)

    msil_equipment_service = MSILEquipmentService(msil_equipment_repository, msil_shift_repository)

    tenant = request.state.tenant
    username = request.state.username

    role = get_role(username,rbac_session)

    return get_shop_report(
        service=msil_equipment_service, 
        query_params=query_params,
        username=username, 
        role=role,
        shop_id=shop_id
    )


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
# folder = "shop_reports/"
    
# def upload_to_s3(view):
#     report_name = "Shop_View_" + str(view).capitalize() + "_View_" + str(uuid.uuid4()) + ".csv"
    
#     s3_client.upload_file(Filename=temp_file_path, Bucket=bucket_name, Key=folder+report_name)

#     return report_name

@authorize(psm_download)
def get_shop_report(**kwargs):
    """Get plans 

    Returns:
        dict: API response with statusCode and required response of lines
    """ 
    try :
        # error_message = "Something went wrong"
        service : MSILEquipmentService  = kwargs["service"]  
        query_params = kwargs["query_params"]
        # username = kwargs["username"]
        shop_id = kwargs["shop_id"]

        # view = query_params.get("view", None)
        machine_group = query_params.get("machine_group", None)
        machine_name = query_params.get("machine_name", None)
        if machine_name:
            machine_name=machine_name.split(",")

        return service.shop_view_report(None, shop_id, machine_name=machine_name, machine_group=machine_group)
        
        # with open(temp_file_path, 'w') as csvfile: 
        #     # creating a csv writer object 
        #     csvwriter = csv.writer(csvfile) 

        #     service.shop_view_report(csvwriter, shop_id, 
        #                              machine_group=machine_group,
        #                              machine_name=machine_name,
        #                              view=view)
        # report_name = upload_to_s3(view)

        # report_url = s3_client.generate_presigned_url(
        #         ClientMethod='get_object', 
        #         Params={'Bucket': bucket_name, 'Key': folder+report_name},
        #         ExpiresIn=3600)
                
        # return aws_helper.lambda_response(200, msg = "Success", data = { "report_url" : report_url })
    
    except Exception as e:
        logger.error("Failed to get shop report", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e)
            }
        )


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
    
#     msil_equipment_repository = MSILEquipmentRepository(session)
#     msil_shift_repository = MSILShiftRepository(rbac_session)

#     msil_equipment_service = MSILEquipmentService(msil_equipment_repository, msil_shift_repository)
    
    
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
#     authenticated_param = event.get("authenticated", False)
#     logger.info(f"authenticated :: {authenticated_param}")

#     role = None
#     if not authenticated_param:
#         role = get_role(username, rbac_session)
#     try:
#         if request_method == "GET":
#             return get_shop_report(service=msil_equipment_service, 
#                                    query_params=query_params, \
#                                     username=username, 
#                                     role=role,
#                                     shop_id=shop_id)
#     except ForbiddenException:
#         return aws_helper.lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")