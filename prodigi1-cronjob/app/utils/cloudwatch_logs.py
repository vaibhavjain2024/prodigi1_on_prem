import logging,os
from datetime import datetime, timezone
from typing import Dict
import requests
import threading
from config.app_config import SERVICE_NAME, IS_LOG_SEND_TO_CW, AWS_API_GATEWAY_KEY, SYNC_BASE_GATEWAY_URL_LISTS, AWS_CLOUD_WATCH_URL

def get_healthy_sync_gateway_base_url():
    base_url_list = SYNC_BASE_GATEWAY_URL_LISTS
    sync_base_url = None
    for base_url in base_url_list:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": AWS_API_GATEWAY_KEY
        }
        logging.info(f"Check health of SYNC_GATEWAY_BASE_URL {base_url}")
        publish_cloud_watch_url = base_url+"/prodigi1/sync/cloud-watch/logs"
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec='seconds'),
            "service_name": SERVICE_NAME,
            "log_type": "INFO",
            "message": f"{base_url} Sync base url is healthy.",
            "kwargs": {}
        }
        try:
            response = requests.post(publish_cloud_watch_url, json=log_data, headers=headers)
            logging.info(f"Response from SYNC_GATEWAY_BASE_URL {base_url} : {response}")
            response.raise_for_status()
            sync_base_url = base_url
            # set HEALTHY_SYNC_BASE_URL in os environment
            os.environ["HEALTHY_SYNC_CW_ENDPOINT"] = publish_cloud_watch_url
            logging.warning(f"Healthy SYNC_GATEWAY_BASE_URL is {base_url}")
            break
        except Exception as e:
            logging.error(f"Unhealty SYNC_GATEWAY_BASE_URL : {str(e)}", exc_info=True)
            logging.error(f"Unhealty SYNC_GATEWAY_BASE_URL : {str(e)}")
    if sync_base_url is None:
        logging.warning (f"All SYNC_GATEWAY_BASE_URL are Unhealthy {base_url_list}")
    return sync_base_url

def call_log_in_thread(log_type: str, log_message: str, **kwargs):
    # Check if CloudWatch logging is enabled in the config
    if not IS_LOG_SEND_TO_CW:
        return

    log_data: Dict[str, str] = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec='seconds'),
        "service_name": SERVICE_NAME,
        "log_type": log_type.upper(),
        "message": log_message,
        "kwargs": {}
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key":AWS_API_GATEWAY_KEY
    }

    # Send the log data to the Lambda via API Gateway
    cloud_watch_post_endpoint = os.environ.get("HEALTHY_SYNC_CW_ENDPOINT", AWS_CLOUD_WATCH_URL)
    try:
        response = requests.post(cloud_watch_post_endpoint, json=log_data, headers=headers)
        # Raise an error if the response status is not successful
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Unexpected error while logging to CloudWatch: {str(e)} endpoint i.e {cloud_watch_post_endpoint}")
        get_healthy_sync_gateway_base_url()
    # Return without raising any errors to ensure the API continues working
    return


def log_to_cloudwatch(log_type: str, log_message: str, **kwargs):
    # Create a thread for the log_to_cloudwatch function
    thread = threading.Thread(target=call_log_in_thread, args=(log_type, log_message), kwargs=kwargs)
    # Start the thread
    thread.start()
