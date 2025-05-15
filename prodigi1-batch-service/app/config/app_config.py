from dotenv import load_dotenv
import os

ENV = os.getenv("ENV", "dev")

# Load the appropriate .env file
env_file = f".env.{ENV}"
load_dotenv(env_file)


ROUTE_PREFIX = f"/{ENV}/prodigi1/sync"
TENANT = os.getenv("TENANT","MSIL")
AWS_API_GATEWAY_KEY = os.getenv("AWS_API_GATEWAY_KEY","development")
SYNC_BASE_GATEWAY_URL_LISTS = os.getenv("SYNC_BASE_GATEWAY_URL_LISTS", "").split(",")

# Cloudwatch logs Configuration
SYNC_GATEWAY_BASE_URL=os.getenv("SYNC_GATEWAY_BASE_URL","https://sruibwvkxf.execute-api.ap-south-1.amazonaws.com")
SERVICE_NAME = "prodigi1-batch-service"
IS_LOG_SEND_TO_CW = os.getenv("IS_LOG_SEND_TO_CW",False)
LOG_GROUP_NAME="/aws/lambda/msil-iot-psm-on-prem-logs"
AWS_CLOUD_WATCH_URL=f"{SYNC_GATEWAY_BASE_URL}/pressShop/sync/cloud-watch/logs"

# Sync
SYNC_ADFS_GATEWAY_USERS_URL=os.getenv("SYNC_ADFS_GATEWAY_USERS_URL", "https://qczgq0f299.execute-api.ap-south-1.amazonaws.com")
SYNC_GET_DATA_FROM_SQS_URL = f"{SYNC_GATEWAY_BASE_URL}/pressShop/sync/consume/sqs/data"
SYNC_ADFS_USERS_URL = f"{SYNC_ADFS_GATEWAY_USERS_URL}/platform/sync/procheck2/adfs-users"

# Postgres DB connection
PSM_CONNECTION_STRING = os.getenv("PSM_CONNECTION_STRING")
PLATFORM_CONNECTION_STRING = os.getenv("PLATFORM_CONNECTION_STRING")

DELETE_DAY_VAL = int(os.getenv("DELETE_DAY_VAL","7"))
