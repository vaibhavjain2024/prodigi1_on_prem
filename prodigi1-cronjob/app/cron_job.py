import requests,traceback
from datetime import datetime, timedelta
from utils.cloudwatch_logs import log_to_cloudwatch
from utils.logger_utility import logger

async def call_sync_data(api_url, cron_job_id, start_time, method_type="POST", model_name=None):
    """Calls the FastAPI route with cron_job_id and start_time."""
    response = None
    try:
        print(f"call_sync_data for method type : {method_type}  API URL : {api_url} and model name {model_name}")
        if method_type == "GET":
            response = requests.get(api_url, params={})
        elif method_type == "POST" :
            log_to_cloudwatch("INFO", f"api url {api_url}")
            response = requests.post(api_url, params={
                "cron_job_id": str(cron_job_id),
                "start_time": str(start_time)
            })
        elif method_type == "DELETE" and model_name:
            message = f"DELETE url {api_url} and model_name {model_name}"
            logger.info(message)
            log_to_cloudwatch("INFO", message)
            response = requests.delete(api_url,params={"model_name":model_name})
        elif method_type == "DELETE":
            message = f"DELETE url {api_url}"
            logger.info(message)
            log_to_cloudwatch("INFO", message)
            response = requests.delete(api_url, params={
                "cron_job_id": str(cron_job_id),
                "start_time": str(start_time)
            })
        if response and response.status_code == 200:
            log_to_cloudwatch("INFO", f"API Call Success: {response.json()}")
            return True
        else:
            log_to_cloudwatch("INFO", f"API Call Failed: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        log_to_cloudwatch("INFO", f"Error while calling API: {str(e)}")
