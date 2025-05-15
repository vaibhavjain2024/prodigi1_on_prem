from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

# from IAM.authorization.psm_admin_authorizer import admin
# from IAM.authorization.psm_shop_authorizer import shop_auth
# from IAM.exceptions.forbidden_exception import ForbiddenException

# from app.modules.IAM.role import get_role

from app.modules.common.logger_common import get_logger

#  from metrics_logger import log_metrics_to_cloudwatch
# import constants, aws_utils
# from aws_helper import lambda_response

from app.modules.PSM.repositories.msil_master_repository import MSILDigiprodMasterRepository
from app.modules.PSM.services.msil_master_service import MSILMasterService
from app.modules.PSM.session_helper import get_session_helper, SessionHelper
# from json_utils import default_format_for_json


logger = get_logger()

def handler(shop_id):
    # session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
    # session = session_helper.get_session()

    session = SessionHelper(PSM_CONNECTION_STRING).get_session()

    # rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
    # rbac_session = rbac_session_helper.get_session()

    repository = MSILDigiprodMasterRepository(session)
    service = MSILMasterService(repository)

    return service.get_masters(shop_id)


# @log_metrics_to_cloudwatch
# def lambda_handler(event, context):
#     logger.info(f"Event received at msil-iot-psm-master-file-details: {event}")

#     PSM_CONNECTION_STRING = "PSM_CONNECTION_STRING"
#     PLATFORM_CONNECTION_STRING = "PLATFORM_CONNECTION_STRING"

#     session_helper = get_session_helper(PSM_CONNECTION_STRING, PSM_CONNECTION_STRING)
#     session = session_helper.get_session()
#     rbac_session_helper = get_session_helper(PLATFORM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING)
#     rbac_session = rbac_session_helper.get_session()
#     repository = MSILDigiprodMasterRepository(session)
#     service = MSILMasterService(repository)

#     username = event.get('requestContext',{}) \
#                         .get('authorizer',{}) \
#                         .get('claims',{}) \
#                         .get('cognito:username',"MSIL")

#     try:

#         shop_id = event["queryStringParameters"].get("shop_id")

#         if not shop_id:
#             return lambda_response(
#                 status_code=406,
#                 data={
#                     "response": {},
#                     "responseCode": constants.STATUS_CODES.get(
#                         constants.PARAMETER_MISSING
#                     ),
#                 },
#                 msg="Shop ID required",
#             )

#         try:
#             role = get_role(username, rbac_session)
#             shop_auth(role=role, shop_id=shop_id)
#             admin(role=role)
#         except ForbiddenException:
#             return lambda_response(status_code = 403, data={},msg="Forbidden, shop not accessible")

#         response = service.get_masters(shop_id)
        
#         if not response:
#             return lambda_response(
#                 status_code=204,
#                 data={
#                     "response": {},
#                     "responseCode": constants.STATUS_CODES.get(constants.NO_CONTENT),
#                 },
#                 msg="No content found",
#             )

#         return {
#             'statusCode': 200,
#             'body': json.dumps(response,
#             default=default_format_for_json)
#         }

#     except Exception:
#         logger.error(f"Error occurred while fetching master details.", exc_info=True)
#         return lambda_response(
#             status_code=503,
#             data={
#                 "response": {},
#                 "responseCode": constants.STATUS_CODES.get(constants.SERVER_ERROR),
#             },
#             msg="Failed to fetch details, contact admin",
#         )
