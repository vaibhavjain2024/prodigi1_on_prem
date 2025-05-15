import datetime
import traceback
from fastapi import HTTPException, status
from app.config.app_config import SYNC_ADFS_USERS_URL, PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING
from modules.IAM.session_helper import SessionHelper
from app.utils.common_utility import fetch_data_from_cloud
from app.utils.cloudwatch_logs import log_to_cloudwatch
from app.utils.logger_utility import logger
from app.utils import constants


# async def sync_users_data(messages, cron_job_id, start_time):
#     sync_data = []
#     try:
#         cron_data = {
#             "job_id": cron_job_id,
#             "sync_category": "user-data",
#             "sync_data": sync_data,
#             "status": constants.INPROGRESS,
#             "error": "",
#             "start_time": start_time
#         }
#         # await insert_data_in_cron_job(cron_data)

#         logger.info(f"User data received from SQS: {messages}")
#         log_to_cloudwatch("INFO", f"User data received from SQS: {messages}")

#         for data in messages:
#             message_data = data["Body"]
#             action_value = ""

#             if "permissions" in message_data:
#                 del message_data["permissions"]
#             if 'MessageAttributes' in data and 'Action' in data['MessageAttributes']:
#                 action_value = data['MessageAttributes']['Action']

#             message_data["username"] = message_data["username"].split("\\")[-1].lower()

#             logger.info(f"Action attribute value:- {action_value} and Username is {message_data['username']}")
#             # log_to_cloudwatch("INFO", f"Action attribute value:- {action_value} and Username is {message_data['username']}")

#             [permission.pop("shop_details", None) for permission in message_data["role"]["permissions"]]
#             logger.info("shop_details removed")

#             if action_value == "update":
#                 try:
#                     logger.info(f"Updating user {message_data['username']}record..")
#                     log_to_cloudwatch("INFO", f"Updating user {message_data['username']}record..")
#                     result = await update_user_record_in_mongo({"username": message_data["username"]}, message_data)
#                     if result.matched_count == 0:
#                         await insert_user_record_in_mongo(message_data)
#                 except Exception as e:
#                     logger.info("Record does not exist. So inserting new record.")
#                     await insert_user_record_in_mongo(message_data)
#             elif action_value == "create":
#                 try:
#                     logger.info(f"Creating new User {message_data['username']} Record...")
#                     log_to_cloudwatch("INFO", f"Creating new User {message_data['username']} Record...")
#                     result = await insert_user_record_in_mongo(message_data)
#                 except Exception as e:
#                     if '_id' in message_data:
#                         print(f"Removing _id: {message_data['_id']}")
#                         del message_data['_id']
#                     logger.info("User was already exist. So updating user record..")
#                     await update_user_record_in_mongo({"username": message_data["username"]}, message_data)
#             elif action_value == "delete":
#                 logger.info(f"deleting the user record {message_data['username']}")
#                 log_to_cloudwatch("INFO", f"deleting the user record {message_data['username']}")
#                 await delete_user_record_from_mongo({"username": message_data["username"]})

#             sync_data.append(message_data)
        
#         cron_data = {
#             "sync_category": "user-data",
#             "sync_data": sync_data,
#             "status": constants.SUCCESS,
#             "error": "",
#             "end_time": datetime.datetime.now()
#         }
#         await update_cron_job({"job_id": cron_job_id}, cron_data)

#         status_code = status.HTTP_200_OK
#         message = "User updated successfully."
#         return status_code, message
#     except Exception as e:
#         exception_traceback = traceback.format_exc()
#         logger.error(exception_traceback)
#         log_to_cloudwatch("ERROR", exception_traceback)
#         cron_data = {
#             "sync_category": "user-data",
#             "sync_data": sync_data,
#             "status": constants.FAILED,
#             "error": str(e)
#         }
#         await update_cron_job({"job_id": cron_job_id}, cron_data)
#         raise Exception(f"Some problem occurred while performing crud operations on user data.{e}")


async def sync_adfs_users_data(user_service, permission_service):

    try:
        all_users_synced = False
        page_number = 1
        data = {
            "page_size": constants.PAGE_SIZE
        }
        
        while not all_users_synced:
            data["page_number"] = page_number
            logger.info(f"data for sync user: {data}")
            users_records = await fetch_data_from_cloud(SYNC_ADFS_USERS_URL, data=data)
            message = f"fetch_user_data_from_cloud_db {users_records}"
            logger.info(message)

            if "users" in users_records:
                for user in users_records["users"]:
                    user["username"] = user["username"].split("\\")[-1].lower()
                    if user["username"] == "dilpreet":
                        user_service.create_user_with_roles(user)
                        for permission in user.get("role", {}).get("permissions", []):
                            permission_service.create_permission(permission)
                    
            if "success" in users_records.get("message", "") or not users_records["users"]:
                # all_users_synced = True
                message = "All data synced successfully."
                status_code = 200
                return status_code, message
            
            page_number = users_records.get("next_page_number")
            print('page_number', page_number)
        else:
            message = "Data not synced ."
            status_code = 400
            return status_code, message

    except Exception as e:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)
        raise Exception(e)

