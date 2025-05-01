
import os
import json
from dotenv import load_dotenv

ENV = os.getenv("ENV", "local")

# Load the appropriate .env file
env_file = f".env.{ENV}"
load_dotenv(env_file)

ROUTE_PREFIX =  f"/{ENV}/prodigi1/on-prem"

# Cloudwatch logs Configuration
SYNC_GATEWAY_BASE_URL=os.getenv("SYNC_GATEWAY_BASE_URL","https://sruibwvkxf.execute-api.ap-south-1.amazonaws.com")
AWS_CLOUD_WATCH_URL=f"{SYNC_GATEWAY_BASE_URL}/prodigi1/sync/cloud-watch/logs"
LOG_GROUP_NAME="/aws/lambda/msil-iot-prodigi1-on-prem-logs"
IS_LOG_SEND_TO_CW = os.getenv("IS_LOG_SEND_TO_CW",False)
SERVICE_NAME = "prodigi1-on-prem-service"

# Mongo DB connection
PSM_CONNECTION_STRING = os.getenv("PSM_CONNECTION_STRING")
PLATFORM_CONNECTION_STRING = os.getenv("PLATFORM_CONNECTION_STRING")
