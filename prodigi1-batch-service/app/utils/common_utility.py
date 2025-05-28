from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.config.app_config import AWS_API_GATEWAY_KEY #AWS_SYNC_SHOP_PLANT_API_URL
from app.utils.cloudwatch_logs import log_to_cloudwatch
from importlib import reload
from app.config import app_config
from app.utils.logger_utility import logger
import traceback
import requests
import httpx

def reload_config():
    reload(app_config)

def create_response(status_code: int, msg: str, data: dict):
    content={
        "response": data,
        "responseCode": status_code,
        "message": msg,
    },
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, Content-Type, Authorization",
            "Access-Control-Allow-Methods": "POST, PUT, GET, OPTIONS, DELETE",
        }
    )

async def fetch_data_from_cloud(data_url, data=None, params=None):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": AWS_API_GATEWAY_KEY
    }
    try:
        message = f"Fetching data from end point {data_url}"
        print("==========",message)
        logger.info(message)
        log_to_cloudwatch("INFO", message)
        checksheet_response = requests.get(data_url, json=data, headers=headers, params=params)
        print("***********", checksheet_response)
        logger.info(f"cloud response: {checksheet_response}")
        checksheet_records = checksheet_response.json()
        message = f"Response received:- {len(checksheet_records)}"
        logger.info(message)
        log_to_cloudwatch("INFO", message)
        return checksheet_records
    except Exception as e:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        reload_config()
        log_to_cloudwatch("ERROR", exception_traceback)
        logger.info("Error occured while fetch data from cloud", exc_info=True)
        raise HTTPException(status_code=500, detail=f"API Gateway error while getting data: {str(e)}")


async def send_filled_checksheet_data(checksheet_data_url, data, params={}, headers={}):
    headers.update({
        "x-api-key": AWS_API_GATEWAY_KEY
    })
    try:
        message = f"Calling Checksheet sync api for url :- {checksheet_data_url}"
        logger.info(message)
        log_to_cloudwatch("INFO", message)
        async with httpx.AsyncClient() as client:
            checksheet_response = await client.post(checksheet_data_url, json=data, params=params, headers=headers)
        checksheet_records = checksheet_response.json()
        # Check for status code in the response
        if checksheet_response.status_code == 404:
            return {"responseCode": 404, "error": "Not Found"}
        return checksheet_records
    except Exception as e:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        reload_config()
        log_to_cloudwatch("ERROR", exception_traceback)
        raise HTTPException(status_code=500, detail=f"API Gateway error while sending data: {str(e)}")
    
    
# async def get_shops_plants_data():
#     headers = {
#         "x-api-key": AWS_API_GATEWAY_KEY
#     }
#     try:
#         async with httpx.AsyncClient() as client:
#             shops_plants_data_response = await client.get(AWS_SYNC_SHOP_PLANT_API_URL, params={}, headers=headers)
#         shops_plants_data_records = shops_plants_data_response.json()
#         return shops_plants_data_records
#     except Exception as e:
#         reload_config()
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Shops and Plants Sync API Gateway error: {str(e)}")


def json_serialize_object_ids(obj):
    """
    Recursively convert all ObjectId instances to strings in a nested dictionary or list.
    """
    if isinstance(obj, dict):
        return {k: json_serialize_object_ids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serialize_object_ids(item) for item in obj]
    # elif isinstance(obj, ObjectId):
    #     return str(obj)
    else:
        return obj
