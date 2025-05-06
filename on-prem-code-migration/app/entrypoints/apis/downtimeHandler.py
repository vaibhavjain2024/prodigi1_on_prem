from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from app.schema.downtimeSchema import (
    getDowntime,
    getDowntimeFilter,
    getDowntimeReport,
    updateDowntimeRemark
)

from app.onPremServices.downtime import (
    msil_iot_psm_downtime_remark_list,
    msil_iot_psm_downtime_remark_update,
    msil_iot_psm_get_downtime_filters,
    msil_iot_psm_get_downtime_report,
    msil_iot_psm_get_downtime,
    msil_iot_psm_get_total_downtime
)

from app.utils.auth_utility import jwt_required

router = APIRouter(prefix="/pressShop/downtime")

def returnJsonResponses(response):
    return JSONResponse(content=response, status_code=200)


@router.get('/')
@jwt_required
async def get_downtime(request: Request, downtime: getDowntime = Depends()):
    shop_id = downtime.shop_id
    page_no = downtime.page_no
    page_size = downtime.page_size

    if not shop_id or not page_no or not page_size:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' / 'page_no' / 'page_size' query parameters")

    query_params = downtime.model_dump(exclude={"shop_id", "page_no", "page_size"}, exclude_none=True)
    response = msil_iot_psm_get_downtime.handler(shop_id, page_no, page_size, request, **query_params)
    return returnJsonResponses(response)


@router.get('/filters')
@jwt_required
async def get_downtime_filters(request: Request, downtimefilter: getDowntimeFilter = Depends()):
    shop_id = downtimefilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_downtime_filters.handler(shop_id, request)
    return returnJsonResponses(response) 


@router.get('/report')
@jwt_required
async def get_downtime_report(request: Request, downtimereport: getDowntimeReport = Depends()):
    shop_id = downtimereport.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = downtimereport.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_downtime_report.handler(shop_id, request, **query_params)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=downtime_report.csv"})


@router.get('/totalduration')
@jwt_required
async def get_downtime_total_duration(request: Request, downtimereport: getDowntimeReport = Depends()):
    shop_id = downtimereport.shop_id

    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = downtimereport.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_total_downtime.handler(shop_id, request, **query_params)
    return returnJsonResponses(response) 


@router.get('/remark/list')
@jwt_required
async def get_downtime_remark_list(request: Request, downtimefilter: getDowntimeFilter = Depends()):
    shop_id = downtimefilter.shop_id

    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_downtime_remark_list.handler(shop_id, request)
    return returnJsonResponses(response)


@router.put('/remark/update')
@jwt_required
async def put_downtime_remark(request: Request, downtime: updateDowntimeRemark):
    shop_id = downtime.shop_id
    id = downtime.id
    remarks = downtime.remarks
    comment = downtime.comment

    if not shop_id or not id or not remarks or not comment:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' / 'id' / 'remark' / 'comment' query parameters")
    
    response = msil_iot_psm_downtime_remark_update.handler(shop_id, id, remarks, comment, request)
    return returnJsonResponses(response)