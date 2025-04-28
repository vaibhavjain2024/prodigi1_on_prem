from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from schema.planSchema import (
    getPlan,
    getPlanFilter,
    getPlanReport,
    planDownload,
    planUpload
)

from onPremServices.plan import (
    msil_iot_psm_get_alerts,
    msil_iot_psm_get_file_status,
    msil_iot_psm_get_plan_filters,
    msil_iot_psm_get_plan_report,
    msil_iot_psm_get_plan,
    msil_iot_psm_get_psm_signed_url_to_download_plan_file,
    msil_iot_psm_get_psm_signed_url_to_upload_plan_file
)

router = APIRouter(prefix="/pressShop")

def returnJsonResponses(response):
    return JSONResponse(content=response, status_code=200)


@router.get('/plan')
async def get_plan(plan: getPlan = Depends()):
    shop_id = plan.shop_id
    page_no = plan.page_no
    page_size = plan.page_size

    if not shop_id or not page_no or not page_size:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' / 'page_no' / 'page_size' query parameters")

    query_params = plan.model_dump(exclude={"shop_id", "page_no", "page_size"}, exclude_none=True)
    response = msil_iot_psm_get_plan.handler(shop_id, page_no, page_size, **query_params)
    return returnJsonResponses(response)


@router.get('/plan/report')
async def get_plan_report(planreport: getPlanReport = Depends()):
    shop_id = planreport.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = planreport.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_plan_report.handler(shop_id, **query_params)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=plan_report.csv"})


@router.get('/alerts')
async def get_alerts(alertfilter: getPlanFilter = Depends()):
    shop_id = alertfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_alerts.handler(shop_id)
    return returnJsonResponses(response)


@router.get('/plan/filters')
async def get_plan_filters(alertfilter: getPlanFilter = Depends()):
    shop_id = alertfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_plan_filters.handler(shop_id)
    return returnJsonResponses(response) 


@router.get('/plan/status')
async def get_plan_status(alertfilter: getPlanFilter = Depends()):
    shop_id = alertfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")

    response = msil_iot_psm_get_file_status.handler(shop_id)
    return returnJsonResponses(response) 


@router.get('/plan/download')
async def get_plan_file_download(plandownload: planDownload = Depends()):
    shop_id = plandownload.shop_id
    shop_name = plandownload.shop_name
    date = plandownload.date

    response = msil_iot_psm_get_psm_signed_url_to_download_plan_file.handler(shop_id, shop_name, date)
    return returnJsonResponses(response) 


@router.get('/plan/upload')
async def get_plan_file_upload(planupload: planUpload = Depends()):
    shop_id = planupload.shop_id
    shop_name = planupload.shop_name
    
    response = msil_iot_psm_get_psm_signed_url_to_upload_plan_file.handler(shop_id, shop_name)
    return returnJsonResponses(response) 