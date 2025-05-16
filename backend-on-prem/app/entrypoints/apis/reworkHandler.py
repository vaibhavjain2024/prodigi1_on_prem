from fastapi import Request, Depends, HTTPException
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
from app.utils.auth_utility import jwt_required
from app.utils.common_utility import returnJsonResponse

router = APIRouter(prefix="/pressShop/rework")


@router.get("/")
@jwt_required
async def quality_updation(request: Request, quality: getQuality = Depends()):
    shop_id = quality.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = quality.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_quality_updation.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)

@router.get("/report")
@jwt_required
async def quality_updation_report(request: Request, getreport: getReport = Depends()):
    shop_id = getreport.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = getreport.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_quality_updation_report.handler(shop_id, request, **query_params)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})

@router.put("/updation")
@jwt_required
async def quality_updation_records_update(request: Request, updaterecord: updateRecord):
    punching_id = updaterecord.punching_id
    updation_list = updaterecord.updation_list
    if not punching_id or not updation_list:
        raise HTTPException(status_code=400, detail="Missing 'punching_id' / 'updation_list' query parameter")
    
    response = msil_iot_psm_quality_updation_records_update.handler(punching_id, updation_list, request)
    return returnJsonResponse(response)

@router.post("/submit")
@jwt_required
async def quality_updation_submission(request: Request, addrecord: addRecord):
    punching_id = addrecord.punching_id
    if not punching_id :
        raise HTTPException(status_code=400, detail="Missing 'punching_id' query parameter")
    
    response = msil_iot_psm_quality_updation_submission.handler(punching_id, request)
    return returnJsonResponse(response)

@router.get("/total")
@jwt_required
async def quality_updation_total_rework(request: Request, totalrework: reworkTotal = Depends()):
    shop_id = totalrework.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    query_params = totalrework.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_quality_updation_total_rework_qty.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)

@router.get("/records")
@jwt_required
async def quality_updation_records(request: Request, getrecord: getRecord = Depends()):
    punching_id = getrecord.punching_id
    if not punching_id :
        raise HTTPException(status_code=400, detail="Missing 'punching_id' query parameter")
    
    response = msil_iot_psm_get_quality_updation_records.handler(punching_id, request)
    return returnJsonResponse(response)