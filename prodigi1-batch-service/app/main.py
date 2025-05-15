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

# Initialize the Prometheus Instrumentator
instrumentator = Instrumentator()
# Instrument your FastAPI app
instrumentator.instrument(app).expose(app, "/metrics")

app.include_router(sync_users.router, prefix=ROUTE_PREFIX, tags=["Sync user"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Prodigi1 Batch Service"}

# Expose Prometheus metrics at '/metrics' endpoint
@app.get("/metrics")
async def metrics():
    # Prometheus metrics will be automatically exposed
    return JSONResponse(content={"message": "Metrics endpoint"})