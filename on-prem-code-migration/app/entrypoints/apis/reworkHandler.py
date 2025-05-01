from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from app.schema.reworkSchema import (
    getQuality, reworkTotal, getReport,
    addRecord, updateRecord, getRecord
)

from app.onPremServices.reWork import (
    msil_iot_psm_get_quality_updation, msil_iot_psm_quality_updation_records_update,
    msil_iot_psm_quality_updation_submission, msil_iot_psm_quality_updation_total_rework_qty,
    msil_iot_psm_get_quality_updation_records, msil_iot_psm_get_quality_updation_report
)

router = APIRouter(prefix="/pressShop/rework")

def returnJsonResponse(response):
    return JSONResponse(content=response, status_code=200)

@router.get("/")
async def quality_updation(quality: getQuality = Depends()):
    shop_id = quality.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = quality.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_quality_updation.handler(shop_id, **query_params)
    return returnJsonResponse(response)

@router.get("/report")
async def quality_updation_report(getreport: getReport = Depends()):
    shop_id = getreport.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = getreport.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_quality_updation_report.handler(shop_id, **query_params)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})

@router.put("/updation")
async def quality_updation_records_update(updaterecord: updateRecord):
    punching_id = updaterecord.punching_id
    updation_list = updaterecord.updation_list
    if not punching_id or not updation_list:
        raise HTTPException(status_code=400, detail="Missing 'punching_id' / 'updation_list' query parameter")
    
    response = msil_iot_psm_quality_updation_records_update.handler(punching_id, updation_list)
    return returnJsonResponse(response)

@router.post("/submit")
async def quality_updation_submission(addrecord: addRecord):
    punching_id = addrecord.punching_id
    if not punching_id :
        raise HTTPException(status_code=400, detail="Missing 'punching_id' query parameter")
    
    response = msil_iot_psm_quality_updation_submission.handler(punching_id)
    return returnJsonResponse(response)

@router.get("/total")
async def quality_updation_total_rework(totalrework: reworkTotal = Depends()):
    shop_id = totalrework.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    query_params = totalrework.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_quality_updation_total_rework_qty.handler(shop_id, **query_params)
    return returnJsonResponse(response)

@router.get("/records")
async def quality_updation_records(getrecord: getRecord = Depends()):
    punching_id = getrecord.punching_id
    if not punching_id :
        raise HTTPException(status_code=400, detail="Missing 'punching_id' query parameter")
    
    response = msil_iot_psm_get_quality_updation_records.handler(punching_id)
    return returnJsonResponse(response)