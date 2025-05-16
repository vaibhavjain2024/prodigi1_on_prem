from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime


def json_serialize_convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: json_serialize_convert_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [json_serialize_convert_datetime(item) for item in obj]
    else:
        return obj
    

def returnJsonResponse(response):
    response = json_serialize_convert_datetime(response)
    return JSONResponse(content=response, status_code=200)


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