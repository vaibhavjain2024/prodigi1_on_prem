from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from app.schema.planSchema import (
    getPlan,
    getPlanFilter,
    getPlanReport,
    planDownload,
    planUpload
)

from app.onPremServices.plan import (
    msil_iot_psm_get_alerts,
    msil_iot_psm_get_file_status,
    msil_iot_psm_get_plan_filters,
    msil_iot_psm_get_plan_report,
    msil_iot_psm_get_plan,
    msil_iot_psm_get_psm_signed_url_to_download_plan_file,
    msil_iot_psm_get_psm_signed_url_to_upload_plan_file
)
from app.utils.auth_utility import jwt_required
from app.utils.common_utility import returnJsonResponse

router = APIRouter(prefix="/pressShop")


@router.get('/plan')
@jwt_required
async def get_plan(request: Request, plan: getPlan = Depends()):
    shop_id = plan.shop_id
    page_no = plan.page_no
    page_size = plan.page_size

    if not shop_id or not page_no or not page_size:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' / 'page_no' / 'page_size' query parameters")

    query_params = plan.model_dump(exclude={"shop_id", "page_no", "page_size"}, exclude_none=True)
    response = msil_iot_psm_get_plan.handler(shop_id, page_no, page_size, request, **query_params)
    return returnJsonResponse(response)


@router.get('/plan/report')
@jwt_required
async def get_plan_report(request: Request, planreport: getPlanReport = Depends()):
    shop_id = planreport.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = planreport.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_plan_report.handler(shop_id, request, **query_params)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=plan_report.csv"})


@router.get('/alerts')
@jwt_required
async def get_alerts(request: Request, alertfilter: getPlanFilter = Depends()):
    shop_id = alertfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_alerts.handler(shop_id, request)
    return returnJsonResponse(response)


@router.get('/plan/filters')
@jwt_required
async def get_plan_filters(request: Request, alertfilter: getPlanFilter = Depends()):
    shop_id = alertfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_plan_filters.handler(shop_id, request)
    return returnJsonResponse(response) 


@router.get('/plan/status')
@jwt_required
async def get_plan_status(request: Request, alertfilter: getPlanFilter = Depends()):
    shop_id = alertfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")

    response = msil_iot_psm_get_file_status.handler(shop_id, request)
    return returnJsonResponse(response) 


@router.get('/plan/download')
@jwt_required
async def get_plan_file_download(request: Request, plandownload: planDownload = Depends()):
    shop_id = plandownload.shop_id
    shop_name = plandownload.shop_name
    date = plandownload.date

    response = msil_iot_psm_get_psm_signed_url_to_download_plan_file.handler(shop_id, shop_name, date, request)
    return returnJsonResponse(response) 


@router.get('/plan/upload')
@jwt_required
async def get_plan_file_upload(request: Request, planupload: planUpload = Depends()):
    shop_id = planupload.shop_id
    shop_name = planupload.shop_name
    
    response = msil_iot_psm_get_psm_signed_url_to_upload_plan_file.handler(shop_id, shop_name, request)
    return returnJsonResponse(response) 