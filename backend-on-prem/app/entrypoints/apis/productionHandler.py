from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from io import StringIO
from csv import DictWriter

from app.schema.productionSchema import (
    getProduction,
    UpdateVariantRequest,
    getProductionFilter,
    getProductionQuality,
    ShopIdSchema
)

from app.onPremServices.production import (
    msil_iot_psm_get_production,
    msil_iot_psm_quality_production_start,
    msil_iot_psm_get_production_part_data,
    msil_iot_psm_production_input_material_update,
    msil_iot_psm_production_quality_punch,
    msil_iot_psm_production_update_variant,
    msil_iot_psm_production_update,
)
from app.utils.auth_utility import jwt_required

router = APIRouter(prefix="/pressShop/production")

def returnJsonResponses(response):
    return JSONResponse(content=response, status_code=200)


@router.get('/')
@jwt_required
async def get_production(request: Request, production: getProduction = Depends()):
    shop_id = production.shop_id

    query_params = production.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_production.handler(shop_id, request, **query_params)
    return returnJsonResponses(response)


@router.post('/')
@jwt_required
async def post_production_start(request: Request, productionfilter: getProductionFilter = Depends()):
    body = await request.json()
    shop_id = productionfilter.shop_id
    production_id = productionfilter.production_id
    
    response = msil_iot_psm_quality_production_start.handler(shop_id, production_id, request, **body)
    return returnJsonResponses(response) 


@router.put('/production/update')
@jwt_required
async def update_production(request: Request, productionfilter: getProductionFilter = Depends()):
    shop_id = productionfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = productionfilter.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_production_update.handler(shop_id, request, **query_params)
    return returnJsonResponses(response)


@router.put('/variant')
@jwt_required
async def update_production_variant(request: Request): # UpdateVariantRequest = Depends())
    body = await request.json()
    
    response = msil_iot_psm_production_update_variant.handler(request, **body)
    return returnJsonResponses(response) 


@router.get('/part-data')
@jwt_required
async def get_production_part_data(request: Request, productionfilter: getProductionFilter = Depends()):
    shop_id = productionfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = productionfilter.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_production_part_data.handler(shop_id, request, **query_params)
    return returnJsonResponses(response)


@router.put('/material-update')
@jwt_required
async def update_input_material_production(request: Request, shop: ShopIdSchema = Depends()):
    body = await request.json()
    
    response = msil_iot_psm_production_input_material_update.handler(shop, request, **body)
    return returnJsonResponses(response) 


@router.put('/quality-punch')
@jwt_required
async def update_production_quality(request: Request, productionquality: getProductionQuality = Depends()):
    shop_id = productionquality.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")

    query_params = productionquality.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_production_quality_punch.handler(shop_id, request, **query_params)
    return returnJsonResponses(response) 