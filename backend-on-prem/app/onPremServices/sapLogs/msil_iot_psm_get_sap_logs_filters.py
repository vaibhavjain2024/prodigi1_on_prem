from fastapi import HTTPException
from app.config.config import PSM_CONNECTION_STRING
from app.modules.PSM.session_helper import SessionHelper
from app.modules.digiprod.services.iot_sap_logs_filters import IotSapLogsFilters


def get_downtime_filters_handler(shop_id):
    try:
        db = SessionHelper(PSM_CONNECTION_STRING).get_session()
        service = IotSapLogsFilters(db)
        response = service.get_sap_logs_downtime_filters(
            shop_id=shop_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_plan_filters_handler(shop_id):
    try:
        db = SessionHelper(PSM_CONNECTION_STRING).get_session()
        service = IotSapLogsFilters(db)
        response = service.get_sap_logs_plan_filters(
            shop_id=shop_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_production_filters_handler(shop_id):
    try:
        db = SessionHelper(PSM_CONNECTION_STRING).get_session()
        service = IotSapLogsFilters(db)
        response = service.get_sap_logs_production_filters(
            shop_id=shop_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
