from os import getenv
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from entrypoints.apis import (
    downtimeHandler, planHandler, shopViewHandler, reworkHandler, reportsHandler, qualityHandler, test
)

app = FastAPI(
    title="MSIL Press Shop OnPrem API's",
    description="OnPrem APIs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def appStartUpHandler():
    load_dotenv()
    if None in (getenv('PSM_CONNECTION_STRING'), getenv('PLATFORM_CONNECTION_STRING')):
        raise ValueError("Missing DB connection strings in the .env file.")

app.add_event_handler("startup", appStartUpHandler)

app.include_router(downtimeHandler.router, tags=["Downtime"])
app.include_router(planHandler.router, tags=["Plan"])
app.include_router(shopViewHandler.router, tags=["Shop View"])
app.include_router(reworkHandler.router, tags=["ReWork"])
app.include_router(reportsHandler.router, tags=["Reports"])
app.include_router(qualityHandler.router, tags=["Quality Punching"])
app.include_router(test.router, tags=["test"])
