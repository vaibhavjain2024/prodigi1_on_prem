from fastapi import Depends, HTTPException, Request
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

router = APIRouter(prefix="/pressShop/production")

def returnJsonResponses(response):
    return JSONResponse(content=response, status_code=200)


@router.get('/')
async def get_production(production: getProduction = Depends()):
    shop_id = production.shop_id

    query_params = production.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_production.handler(shop_id, **query_params)
    return returnJsonResponses(response)


@router.post('/')
async def post_production_start(request: Request, productionfilter: getProductionFilter = Depends()):
    body = await request.json()
    shop_id = productionfilter.shop_id
    production_id = productionfilter.production_id
    
    response = msil_iot_psm_quality_production_start.handler(shop_id, production_id, **body)
    return returnJsonResponses(response) 


@router.put('/production/update')
async def update_production(productionfilter: getProductionFilter = Depends()):
    shop_id = productionfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = productionfilter.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_production_update.handler(shop_id, **query_params)
    return returnJsonResponses(response)


@router.put('/variant')
async def update_production_variant(request: Request): # UpdateVariantRequest = Depends())
    body = await request.json()
    
    response = msil_iot_psm_production_update_variant.handler(**body)
    return returnJsonResponses(response) 


@router.get('/part-data')
async def get_production_part_data(productionfilter: getProductionFilter = Depends()):
    shop_id = productionfilter.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")
    
    query_params = productionfilter.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_get_production_part_data.handler(shop_id, **query_params)
    return returnJsonResponses(response)


@router.put('/material-update')
async def update_input_material_production(request: Request, shop: ShopIdSchema = Depends()):
    body = await request.json()
    
    response = msil_iot_psm_production_input_material_update.handler(shop, **body)
    return returnJsonResponses(response) 


@router.put('/quality-punch')
async def update_production_quality(productionquality: getProductionQuality = Depends()):
    shop_id = productionquality.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameters")

    query_params = productionquality.model_dump(exclude={"shop_id"}, exclude_none=True)
    response = msil_iot_psm_production_quality_punch.handler(shop_id, **query_params)
    return returnJsonResponses(response) 