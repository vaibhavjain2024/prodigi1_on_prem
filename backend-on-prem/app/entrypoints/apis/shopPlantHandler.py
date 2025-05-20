from fastapi import Request, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from app.onPremServices.shopPlant import msil_iot_module_get_sites

from app.utils.auth_utility import jwt_required
from app.utils.common_utility import returnJsonResponse

router = APIRouter(prefix="/platform")


@router.get('/sites')
@jwt_required
async def get_sites(request: Request, module_name: str = ""):

    response = msil_iot_module_get_sites.handler(module_name, request)
    return returnJsonResponse(response)

