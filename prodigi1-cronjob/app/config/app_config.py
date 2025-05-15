import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "dev")

# Load the appropriate .env file
env_file = f".env.{ENV}"
load_dotenv(env_file)

AWS_API_GATEWAY_KEY = os.getenv("AWS_API_GATEWAY_KEY","development")
DELETE_CRON_JOB_ENTRY_DAYS = int(os.getenv("DELETE_CRON_JOB_ENTRY_DAYS","7"))
SYNC_BASE_GATEWAY_URL_LISTS = os.getenv("SYNC_BASE_GATEWAY_URL_LISTS", "").split(",")

# Cloudwatch logs Configuration
SYNC_GATEWAY_BASE_URL=os.getenv("SYNC_GATEWAY_BASE_URL","https://sruibwvkxf.execute-api.ap-south-1.amazonaws.com")
SERVICE_NAME = "cronjob-service"
IS_LOG_SEND_TO_CW = os.getenv("IS_LOG_SEND_TO_CW",False)
LOG_GROUP_NAME="/aws/lambda/msil-iot-prodigi1-on-prem-logs"
AWS_CLOUD_WATCH_URL=f"{SYNC_GATEWAY_BASE_URL}/prodigi1/sync/cloud-watch/logs"

# Batch Service API's ENDPOINT
USER_API_URL = os.getenv("USER_API_URL", f"http://prodigi1-batch-service:8002/{ENV}/prodigi1/sync/user-data/sync-job")

# Postgres DB connection
PSM_CONNECTION_STRING = os.getenv("PSM_CONNECTION_STRING")
PLATFORM_CONNECTION_STRING = os.getenv("PLATFORM_CONNECTION_STRING")