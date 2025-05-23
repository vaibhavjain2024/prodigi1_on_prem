from app.modules.common.logger_common import get_logger
from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING, PLATFORM_CONNECTION_STRING

from app.modules.IAM.role import get_role

from app.modules.PSM.session_helper import get_session_helper, SessionHelper
from app.modules.digiprod.services.iot_sap_logs_downtime_service import IOTSapLogsDowntimeService


def handler(start_time, end_time, request, **query_params):
    """Handler function to get downtime

    Args:
        page_no (int): Page number for pagination
        page_size (int): Number of records per page
        request (Request): FastAPI request object
        **query_params: Additional query parameters

    Returns:
        dict: API response with statusCode and required response of lines
    """
    try:
        db = SessionHelper(PSM_CONNECTION_STRING).get_session()

        # Initialize the service and call the get_downtime method
        service = IOTSapLogsDowntimeService(db)
        query_params = query_params or {}
        response = service.fetch_all_sap_logs(
            start_time, end_time, **query_params)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
