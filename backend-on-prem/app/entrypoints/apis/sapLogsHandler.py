from app.modules.common.logger_common import get_logger
from app.utils.common_utility import returnJsonResponse
from app.utils.auth_utility import jwt_required
from app.onPremServices.sapLogs import (
    msil_iot_psm_get_sap_downtime
)
from app.schema.sapLogsSchema import (
    DowntimeSAPLogs
)
from csv import DictWriter
from datetime import datetime
from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from io import StringIO

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

logger = get_logger()


def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO string
    elif isinstance(obj, dict):
        # Recursively convert datetime in dictionaries
        return {key: convert_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        # Recursively convert datetime in lists
        return [convert_datetime(item) for item in obj]
    else:
        # If it's neither datetime, dict nor list, just return the object
        return obj


router = APIRouter(prefix="/pressShop/sap-logs")


@router.get("/downtime")
@jwt_required
async def get_sap_logs_downtime(request: Request, downtime: DowntimeSAPLogs = Depends()):
    try:
        start_time = downtime.start_time
        end_time = downtime.end_time
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, DATETIME_FORMAT)
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, DATETIME_FORMAT)

        # Validate time range
        if start_time and end_time and start_time > end_time:
            raise HTTPException(
                status_code=400, detail="start_time should be less than end_time"
            )

        # Extract filters excluding already extracted ones, start_time and end_time
        query_params = downtime.model_dump(
            exclude={"start_time", "end_time"}, exclude_none=True
        )

        # Service layer handler called with filters
        response = msil_iot_psm_get_sap_downtime.handler(
            start_time, end_time, request, **query_params
        )

        return returnJsonResponse(response)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Failed to get downtime", exc_info=True)
        logger.error(f"Error: {str(e)}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


@router.get("/downtime/report")
@jwt_required
async def get_sap_logs_downtime_report(request: Request, report_view: DowntimeSAPLogs = Depends()):
    try:
        start_time = report_view.start_time
        end_time = report_view.end_time

        # Convert ISO strings to datetime if needed
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, DATETIME_FORMAT)
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, DATETIME_FORMAT)

        # Validate time range
        if start_time and end_time and start_time > end_time:
            raise HTTPException(
                status_code=400, detail="start_time should be less than end_time"
            )

        # Extract filters excluding already extracted ones, start_time and end_time
        query_params = report_view.model_dump(
            exclude={"start_time", "end_time"}, exclude_none=True
        )

        # Service layer handler called with filters
        response = msil_iot_psm_get_sap_downtime.handler(
            start_time, end_time, request, **query_params
        )

        # Format the response properly
        if isinstance(response, dict):
            response.pop("request", None)

        result = StringIO()
        downtime_data = response.get("downtime", [])

        # Debug print
        print("Type of downtime_data:", type(downtime_data))
        if downtime_data:
            print("Type of first item:", type(downtime_data[0]))
            print("First item content:", downtime_data[0])

        # Extract keys if the first item is a dict
        if isinstance(downtime_data, list) and downtime_data and isinstance(downtime_data[0], dict):
            fieldnames = downtime_data[0].keys()
            print("Extracted keys:", list(fieldnames))

        writer = DictWriter(result, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(downtime_data)

        result.seek(0)

        return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
