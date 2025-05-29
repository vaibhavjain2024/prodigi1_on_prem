from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING

from app.modules.PSM.session_helper import SessionHelper
from app.modules.digiprod.services.iot_sap_logs_production_service import IOTSapLogsProductionService


def handler(start_time, end_time, request, **query_params):
    """Handler function to get downtime

    Args:
        request (Request): FastAPI request object
        **query_params: Additional query parameters

    Returns:
        dict: API response
    """
    try:
        db = SessionHelper(PSM_CONNECTION_STRING).get_session()

        service = IOTSapLogsProductionService(db)
        query_params = query_params or {}
        response = service.fetch_all_sap_logs_production(
            start_time, end_time, **query_params)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
