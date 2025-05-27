from app.modules.common.logger_common import get_logger
from app.utils.common_utility import returnJsonResponse
from app.utils.auth_utility import jwt_required
from app.onPremServices.sapLogs import (
    msil_iot_psm_get_sap_downtime, msil_iot_psm_get_sap_logs_plan
)
from app.schema.sapLogsSchema import (
    DowntimeSAPLogs, PlanSAPLogs
)
from datetime import datetime
from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from app.utils.excel_report_generator import excel_report_generator

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

logger = get_logger()


def format_date_time(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    return "", ""


router = APIRouter(prefix="/pressShop/sap-logs")


@router.get("/downtime")
@jwt_required
async def get_sap_logs_downtime(request: Request, downtime: DowntimeSAPLogs = Depends()):
    try:
        start_time = downtime.start_time
        end_time = downtime.end_time
        iot_shop_id = downtime.iot_shop_id

        if iot_shop_id and not isinstance(iot_shop_id, str):
            raise HTTPException(
                status_code=400, detail="iot_shop_id must be a string."
            )

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
        iot_shop_id = report_view.iot_shop_id

        if iot_shop_id and not isinstance(iot_shop_id, str):
            raise HTTPException(
                status_code=400, detail="iot_shop_id must be a string.")

        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, DATETIME_FORMAT)
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, DATETIME_FORMAT)

        if start_time and end_time and start_time > end_time:
            raise HTTPException(
                status_code=400, detail="start_time should be less than end_time")

        query_params = report_view.model_dump(
            exclude={"start_time", "end_time"}, exclude_none=True)

        response = msil_iot_psm_get_sap_downtime.handler(
            start_time, end_time, request, **query_params
        )

        if isinstance(response, dict):
            response.pop("request", None)

        downtime_data = response.get("downtime", [])

        header_mapping = {
            "filename": "File name",
            "data_sent_flag": "File Status",
            "sap_plant_id": "Plant",
            "sap_shop_id": "Shop",
            "data_sent_time": "Date (Legacy Date)",
            "header_material": "Header material",
            "work_center": "Work Center",
            "start_time": "Start Date",
            "end_time": "End Date",
            "duration": "Total time",
            "reason": "Reason",
            "remarks": "Remarks",
            "shift": "Shift",
        }

        excel_headers = [
            "File name", "File Status", "Plant", "Shop", "Date (Legacy Date)",
            "Header material", "Work Center", "Start Date", "Start Time", "End Date", "End Time",
            "Total time", "Reason", "Remarks", "Shift",
            "Group", "No of Rows Per/shop in a day"
        ]

        transformed_data = []
        for item in downtime_data:
            transformed_item = {
                new_key: item.get(orig_key, "") for orig_key, new_key in header_mapping.items()
            }
            transformed_item["Start Date"], transformed_item["Start Time"] = format_date_time(
                item.get("start_time"))
            transformed_item["End Date"], transformed_item["End Time"] = format_date_time(
                item.get("end_time"))
            transformed_item["Group"] = ""
            transformed_item["No of Rows Per/shop in a day"] = ""
            transformed_data.append(transformed_item)

        # --- Build metadata rows ---
        filter_rows = [
            {"label": "Shop", "value": report_view.iot_shop_id or ""},
            {"label": "Shift", "value": report_view.shift or ""},
            {"label": "Start Time", "value": str(start_time) or ""},
            {"label": "End Time", "value": str(end_time) or ""},
            {"label": "Work Center", "value": report_view.work_center or ""},
            {"label": "Reason", "value": report_view.reason or ""},
            {"label": "Header Material", "value": report_view.header_material or ""},
            {"label": "Remarks", "value": report_view.remarks or ""},
            {"label": "File status", "value": report_view.data_sent_flag.value or ""},
        ]

        # --- Generate Excel file ---
        output = excel_report_generator(
            transformed_data=transformed_data,
            excel_headers=excel_headers,
            metadata_kv_rows=filter_rows,
            report_title="IOT to SAP Downtime log report"
        )

        # Format filename
        now_str = datetime.now().strftime("%d%m%Y%H%M%S")
        shop_name = report_view.iot_shop_id or "IOTSHOP"
        filename = f"DowntimeLog_{shop_name}_{now_str}.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/plan")
@jwt_required
async def get_sap_logs_plan(request: Request, plan: PlanSAPLogs = Depends()):
    try:
        scheduled_start = plan.scheduled_start
        scheduled_finish = plan.scheduled_finish

        # Convert ISO strings to datetime if needed
        if isinstance(scheduled_start, str):
            scheduled_start = datetime.strptime(
                scheduled_start, DATETIME_FORMAT)
        if isinstance(scheduled_finish, str):
            scheduled_finish = datetime.strptime(
                scheduled_finish, DATETIME_FORMAT)

        # Validate time range
        if scheduled_start and scheduled_finish and scheduled_start > scheduled_finish:
            raise HTTPException(
                status_code=400, detail="scheduled_start should be less than scheduled_finish"
            )

        # Extract filters excluding already extracted ones, scheduled_start and scheduled_finish
        query_params = plan.model_dump(
            exclude={"scheduled_start", "scheduled_finish"}, exclude_none=True
        )

        # Service layer handler called with filters
        response = msil_iot_psm_get_sap_logs_plan.handler(
            scheduled_start, scheduled_finish, request, **query_params
        )

        return returnJsonResponse(response)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Failed to get plan", exc_info=True)
        logger.error(f"Error: {str(e)}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


@router.get("/plan/report")
@jwt_required
async def get_sap_logs_plan_report(request: Request, plan: PlanSAPLogs = Depends()):
    try:
        scheduled_start = plan.scheduled_start
        scheduled_finish = plan.scheduled_finish

        if isinstance(scheduled_start, str):
            scheduled_start = datetime.strptime(
                scheduled_start, DATETIME_FORMAT)
        if isinstance(scheduled_finish, str):
            scheduled_finish = datetime.strptime(
                scheduled_finish, DATETIME_FORMAT)

        if scheduled_start and scheduled_finish and scheduled_start > scheduled_finish:
            raise HTTPException(
                status_code=400, detail="scheduled_start should be less than scheduled_finish")

        query_params = plan.model_dump(
            exclude={"scheduled_start", "scheduled_finish"}, exclude_none=True
        )

        response = msil_iot_psm_get_sap_logs_plan.handler(
            scheduled_start, scheduled_finish, request, **query_params
        )

        if isinstance(response, dict):
            response.pop("request", None)

        plan_data = response.get("plan", [])

        # --- Header Mapping ---
        header_mapping = {
            "filename": "File Name",
            "data_received_time": "Data Received Time",
            "order_number": "Order Number",
            "order_status": "Order Status",
            "order_type": "Order Type",
            "mrp_controller": "MRP Controller",
            "plant": "Plant",
            "work_center": "Work Center",
            "scheduled_finish": "Scheduled Finish",
            "scheduled_start": "Scheduled Start",
            "production_version": "Production Version",
            "header_material": "Header Material",
            "group": "Group",
            "total_order_quantity": "Total Order Quantity",
            "header_stock": "Header Stock",
            "order_UoM": "Order UoM",
            "header_Sloc": "Header Sloc",
            "item_number": "Item Number",
            "components": "Components",
            "issue_quantity": "Issue Quantity",
            "comp_stock": "Comp. Stock",
            "comp_Uom": "Comp. Uom",
            "comp_Sloc": "Comp. Sloc",
            "co_product": "Co Product",
            "iot_order_processing_status": "IoT Processing Status",
        }

        excel_headers = list(header_mapping.values()) + [
            "Scheduled Start Time", "Scheduled Finish Time"
        ]

        # --- Data Transformation ---
        transformed_data = []
        for item in plan_data:
            transformed_item = {
                new_key: item.get(orig_key, "") for orig_key, new_key in header_mapping.items()
            }

            # Split scheduled_start and scheduled_finish
            start_dt = item.get("scheduled_start")
            finish_dt = item.get("scheduled_finish")

            def format_time(t):
                try:
                    dt = datetime.strptime(
                        t, DATETIME_FORMAT) if isinstance(t, str) else t
                    return dt.strftime("%H:%M:%S")
                except:
                    return ""

            transformed_item["Scheduled Start Time"] = format_time(start_dt)
            transformed_item["Scheduled Finish Time"] = format_time(finish_dt)

            transformed_data.append(transformed_item)

        # --- Metadata Rows (Filters) ---
        filter_rows = [
            {"label": "Shop", "value": plan.iot_shop_id or ""},
            {"label": "Order Status", "value": plan.order_status or ""},
            {"label": "Order Type", "value": plan.order_type or ""},
            {"label": "Work Center", "value": plan.work_center or ""},
            {"label": "Scheduled start", "value": str(
                scheduled_start) if scheduled_start else ""},
            {"label": "Scheduled finish", "value": str(
                scheduled_finish) if scheduled_finish else ""},
            {"label": "IoT Processing Status",
                "value": plan.iot_order_processing_status or ""},
        ]

        # --- Generate Excel File ---
        output = excel_report_generator(
            transformed_data=transformed_data,
            excel_headers=excel_headers,
            metadata_kv_rows=filter_rows,
            report_title="SAP to IOT Plan log report"
        )

        now_str = datetime.now().strftime("%d%m%Y%H%M%S")
        filename = f"PlanLog_{plan.iot_shop_id or 'IOTSHOP'}_{now_str}.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
