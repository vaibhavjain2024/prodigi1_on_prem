import traceback
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.config.app_config import SYNC_GET_DATA_FROM_SQS_URL, PLATFORM_CONNECTION_STRING
from modules.IAM.repositories.user_repository import UserRepository
from modules.IAM.services.user_service import UserService
from modules.IAM.repositories.permissions_repository import PermissionsRepository
from modules.IAM.services.permissions_service import PermissionsService
from modules.IAM.session_helper import SessionHelper
from app.services.sync_user_data_service import sync_adfs_users_data
from app.utils.common_utility import fetch_data_from_cloud
from app.utils.cloudwatch_logs import log_to_cloudwatch
from app.utils.logger_utility import logger
from app.utils import constants


router = APIRouter()


# @router.post("/user-data/sync-job")
# async def sync_user(cron_job_id:str, start_time:str):
#     """
#     Perform insert, update, delete operation in Postgres DB.
#     """
#     log_to_cloudwatch("INFO", f"Event received at user-data/sync-job")
#     try:
#         data = {
#             "sqs_queue": "user_data"
#         }
#         messages_list = await fetch_data_from_cloud(SYNC_GET_DATA_FROM_SQS_URL, params=data)
#         if len(messages_list['messages']) == 0:
#             return JSONResponse(
#                 status_code=status.HTTP_200_OK,
#                 content={
#                     "message": "No messages found",
#                     "responseCode": constants.STATUS_CODES.get(constants.SUCCESS),
#                 }
#             )
#         status_code, message = await sync_users_data(messages_list['messages'], cron_job_id, start_time)
#         if status_code:
#             return JSONResponse(
#                 status_code=status_code,
#                 content={
#                     "message": message,
#                     "responseCode": constants.STATUS_CODES.get(constants.SUCCESS),
#                 }
#             )
#     except Exception as e:
#         exception_traceback = traceback.format_exc()
#         logger.error(exception_traceback)
#         log_to_cloudwatch("ERROR", exception_traceback)
#         return {
#             "response": {},
#             "message": f"Server error, Please contact admin {e}",
#             "responseCode": constants.STATUS_CODES.get(constants.SERVER_ERROR),
#         }


@router.post("/adfs/users-data/sync-job")
async def sync_all_users():
    """
    Perform insert, update, delete, or upsert operation in Postgres DB.

    :param operation_type: str, The type of operation to perform ('insert', 'update', 'upsert', 'delete')
    :param username: str, The username to use for filtering the document
    :param data: dict, Data to insert (only required for insert/upsert)
    :param update_data: dict, Data to update (only required for update/upsert)
    """
    log_to_cloudwatch("INFO", f"Event received at adfs/users-data/sync-job")
    rbac_session = SessionHelper(PLATFORM_CONNECTION_STRING).get_session()  
    user_repository = UserRepository(rbac_session)
    user_service = UserService(user_repository)
    permission_repository = PermissionsRepository(rbac_session)
    permission_service = PermissionsService(permission_repository)

    try:
        status_code, message = await sync_adfs_users_data(user_service, permission_service)
        if status_code:
            return JSONResponse(
                status_code=status_code,
                content={
                    "message": message,
                    "responseCode": constants.STATUS_CODES.get(constants.SUCCESS),
                }
            )
    except Exception as e:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)
        return {
            "response": {},
            "message": f"Server error, Please contact admin {str(e)}",
            "responseCode": constants.STATUS_CODES.get(constants.SERVER_ERROR),
        }
