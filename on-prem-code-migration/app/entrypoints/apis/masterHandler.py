from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from app.schema.masterSchema import getMasters

from app.onPremServices.master import msil_iot_psm_master_file_details

router = APIRouter(prefix="/pressShop/master")

@router.get('/')
async def get_masters(getmaster: getMasters = Depends()):
    shop_id = getmaster.shop_id
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing 'shop_id' query parameter")
    
    response = msil_iot_psm_master_file_details.handler(shop_id)
    return JSONResponse(content=response, status_code=200)