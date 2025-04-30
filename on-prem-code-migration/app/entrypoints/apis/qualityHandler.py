from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from schema.qualityPunchingSchema import (
    getQuality, getQualityFilter,
    qualityPunching, updateQualityPunching
)

from onPremServices.qualityPunching import (
    msil_iot_psm_get_quality_punching, msil_iot_psm_get_quality_punching_filters,
    msil_iot_psm_quality_reason_list, msil_iot_psm_get_quality_punching_records,
    msil_iot_psm_quality_punching_submission, msil_iot_psm_quality_punching_records_update,
    msil_iot_psm_get_quality_punching_report
)

router = APIRouter(prefix="/pressShop/quality")

def returnJsonResponses(response):
    return JSONResponse(content=response, status_code=200)

@router.get('/')
async def get_quality_punching(quality: getQuality = Depends()):
    shop_id = quality.shop_id
    page_no = quality.page_no
    page_size = quality.page_size

    if not shop_id or not page_no or not page_size:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' / 'page_no' / 'page_size' query parameters")

    query_params = quality.model_dump(exclude={"shop_id", "page_no", "page_size"}, exclude_none=True)
    response = msil_iot_psm_get_quality_punching.handler(shop_id, page_no, page_size, **query_params)
    return returnJsonResponses(response)


@router.get('/filters')
async def quality_punching_filters(qualityfilter: getQualityFilter = Depends()):
    shop_id = qualityfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_quality_punching_filters.handler(shop_id)
    return returnJsonResponses(response) 


@router.get('/report')
async def quality_punching_report(qualityfilter: getQualityFilter = Depends()):
    shop_id = qualityfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_get_quality_punching_report.handler(shop_id)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=quality_report.csv"})

@router.get('/reasons')
async def quality_punching_reasons(qualityfilter: getQuality = Depends()):
    shop_id = qualityfilter.shop_id

    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    response = msil_iot_psm_quality_reason_list.handler(shop_id)
    return returnJsonResponses(response) 


@router.get('/records')
async def quality_punching_records(punching: qualityPunching = Depends()):
    punching_id = punching.punching_id

    if not punching_id:
        raise HTTPException(status_code=400, detail="Missing 'punching_id' query parameters")
    
    response = msil_iot_psm_get_quality_punching_records.handler(punching_id)
    return returnJsonResponses(response) 

@router.put('/punching')
async def update_punching_record(punching: updateQualityPunching):
    punching_id = punching.punching_id
    punching_list = punching.punching_list

    if not punching_id or not punching_list:
        raise HTTPException(status_code=400, detail="Missing 'punching_id' / 'punching_list' query parameters")
    
    response = msil_iot_psm_quality_punching_records_update.handler(punching_id, punching_list)
    return returnJsonResponses(response) 

@router.post('/submit')
async def submit_punching_record(punching: qualityPunching):
    punching_id = punching.punching_id

    if not punching_id:
        raise HTTPException(status_code=400, detail="Missing 'punching_id' query parameters")
    
    response = msil_iot_psm_quality_punching_submission.handler(punching_id)
    return returnJsonResponses(response) 