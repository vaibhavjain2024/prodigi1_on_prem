from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.entrypoints.apis import (
    downtimeHandler,
    planHandler,
    productionHandler,
    shopViewHandler,
    reworkHandler,
    reportsHandler,
    qualityHandler,
    shopPlantHandler,
    sapLogsHandler,
    test
)
from app.config import config

app = FastAPI(
    title="MSIL Press Shop OnPrem API's",
    description="OnPrem APIs",
    version="0.1.0",
    docs_url=f"{config.ROUTE_PREFIX}/docs",  # Change swagger docs URL
    redoc_url=f"{config.ROUTE_PREFIX}/redoc",  # Change redoc URL
    openapi_url=f"{config.ROUTE_PREFIX}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def appStartUpHandler():
    if None in [config.PSM_CONNECTION_STRING, config.PLATFORM_CONNECTION_STRING]:
        raise ValueError("Missing DB connection strings in the .env file.")


app.add_event_handler("startup", appStartUpHandler)

app.include_router(downtimeHandler.router, tags=["Downtime"])
app.include_router(planHandler.router, tags=["Plan"])
app.include_router(shopViewHandler.router, tags=["Shop View"])
app.include_router(reworkHandler.router, tags=["ReWork"])
app.include_router(reportsHandler.router, tags=["Reports"])
app.include_router(qualityHandler.router, tags=["Quality Punching"])
app.include_router(productionHandler.router, tags=["Production"])
app.include_router(shopPlantHandler.router, tags=["Platform APIs"])
app.include_router(sapLogsHandler.router, tags=["SAP Logs"])
app.include_router(test.router, tags=["test"])
