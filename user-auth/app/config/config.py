
import os
import json
from dotenv import load_dotenv

ENV = os.getenv("ENV", "dev")

# Load the appropriate .env file
env_file = f".env.{ENV}"
load_dotenv(env_file)

SECRET_KEY = "msil-prodigi1-on-prem"
ALGORITHM = "HS256"
ROUTE_PREFIX =  f"/{ENV}/prodigi1/user"
TEMP_PASSWORD = os.getenv("TEMP_PASSWORD", "")
AES256_ENCRYPT_KEY = os.getenv("AES256_ENCRYPT_KEY", 'm6Cl+NAZ2hqxx8Ulg0WlXR16oiY1zG3O/OyJLKfmbFk=')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")) # 7 days

AWS_API_GATEWAY_KEY = os.getenv("AWS_API_GATEWAY_KEY","development")
SYNC_BASE_GATEWAY_URL_LISTS = os.getenv("SYNC_BASE_GATEWAY_URL_LISTS", "").split(",")

# Cloudwatch logs Configuration
SYNC_GATEWAY_BASE_URL=os.getenv("SYNC_GATEWAY_BASE_URL","https://sruibwvkxf.execute-api.ap-south-1.amazonaws.com")
AWS_CLOUD_WATCH_URL=f"{SYNC_GATEWAY_BASE_URL}/prodigi1/sync/cloud-watch/logs"
LOG_GROUP_NAME="/aws/lambda/msil-iot-prodigi1-on-prem-logs"
IS_LOG_SEND_TO_CW = os.getenv("IS_LOG_SEND_TO_CW",False)
SERVICE_NAME = "prodigi1-user-auth-service"

# Postgres DB connection
PLATFORM_CONNECTION_STRING = os.getenv("PLATFORM_CONNECTION_STRING", "")

# LDAP configuration
LDAP_SERVER =  os.getenv("LDAP_SERVER", "ldap://your-ldap-server")
IS_LDAP_DISABLE = os.getenv("IS_LDAP_DISABLE", True)
