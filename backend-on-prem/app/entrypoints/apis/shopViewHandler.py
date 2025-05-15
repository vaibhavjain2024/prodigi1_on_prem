from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from app.schema.shopViewSchema import (
    shopView, shopViewGraph, shopViewReport, 
    machineView, machineViewGraph, 
    uniquePartsCount, topBreakDown
)

from app.onPremServices.shopView import (
    msil_iot_psm_get_shop_view, msil_iot_psm_get_shop_view_graph, msil_iot_psm_get_shop_view_report,
    msil_iot_psm_get_machine_view, msil_iot_psm_get_machine_trend_graph,
    msil_iot_psm_unique_parts_count, msil_iot_psm_top_downtime_reasons
)
from app.utils.auth_utility import jwt_required

router = APIRouter(prefix="/pressShop/shop-view")

def returnJsonResponse(response):
    return JSONResponse(content=response, status_code=200)

@router.get("/")
@jwt_required
async def get_shop_view(request: Request, shopview: shopView = Depends()):
    
    shop_id = shopview.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = shopview.model_dump(exclude={"shop_id"}, exclude_none=True)

    response = msil_iot_psm_get_shop_view.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)

@router.get("/report")
@jwt_required
async def get_shop_view_report(request: Request, reportView: shopViewReport = Depends()):
    shop_id = reportView.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    query_params = reportView.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_shop_view_report.handler(shop_id, request, **query_params)

    result = StringIO()
    fieldnames = response[0].keys()

    writer = DictWriter(result, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(response)

    result.seek(0)

    return StreamingResponse(result, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})

@router.get("/graph")
@jwt_required
async def get_shop_view_graph(request: Request, shopviewgraph: shopViewGraph = Depends()):
    shop_id = shopviewgraph.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = shopviewgraph.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_shop_view_graph.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)

@router.get("/uniquecounts")
@jwt_required
async def get_uniquePartscounts(request: Request, uniqueparts: uniquePartsCount = Depends()):
    shop_id = uniqueparts.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    response = msil_iot_psm_unique_parts_count.handler(shop_id, request)
    return returnJsonResponse(response)

@router.get("/topbreakdown")
@jwt_required
async def get_topbreakdown(request: Request, topbreakdown: topBreakDown = Depends()):
    shop_id = topbreakdown.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")

    query_params = topbreakdown.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_top_downtime_reasons.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)

@router.get("/machine")
@jwt_required
async def get_machines(request: Request, machineview: machineView = Depends()):
    shop_id = machineview.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    query_params = machineview.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_machine_view.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)

@router.get("/machine-trend")
@jwt_required
async def get_machine_trend(request: Request, machineviewgraph: machineViewGraph = Depends()):
    shop_id = machineviewgraph.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    query_params = machineviewgraph.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_machine_trend_graph.handler(shop_id, request, **query_params)
    return returnJsonResponse(response)