from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from app.schema.masterSchema import getMasters

from app.onPremServices.master import msil_iot_psm_master_file_details

from app.utils.auth_utility import jwt_required

router = APIRouter(prefix="/pressShop/master")

@router.get('/')
@jwt_required
async def get_masters(request: Request, getmaster: getMasters = Depends()):
    shop_id = getmaster.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    response = msil_iot_psm_master_file_details.handler(shop_id, request)
    return JSONResponse(content=response, status_code=200)