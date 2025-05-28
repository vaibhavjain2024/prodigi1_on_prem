from fastapi import FastAPI
from app.api.cloud_to_on_prem import (
    sync_users
)
from app.config.app_config import ROUTE_PREFIX
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import JSONResponse


app = FastAPI(
    title="MSIL Prodigi1 ON PREM",
    version="0.1.0",
    docs_url=f"{ROUTE_PREFIX}/docs",  # Change swagger docs URL
    redoc_url=f"{ROUTE_PREFIX}/redoc",  # Change redoc URL
    openapi_url=f"{ROUTE_PREFIX}/openapi.json"
    )

app.include_router(sync_users.router, prefix=ROUTE_PREFIX, tags=["Sync user"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Prodigi1 Batch Service"}