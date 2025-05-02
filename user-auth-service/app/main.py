from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import JSONResponse
from app.utils.rate_limiter import limiter
from app.api import auth
from app.config import config
import uvicorn

app = FastAPI(
    title="MSIL Press Shop User Authentication API's",
    version="0.1.0",
    docs_url=f"{config.ROUTE_PREFIX}/docs",  # Change swagger docs URL
    redoc_url=f"{config.ROUTE_PREFIX}/redoc",  # Change redoc URL
    openapi_url=f"{config.ROUTE_PREFIX}/openapi.json"
    )

# Add the limiter to the app state
app.state.limiter = limiter

# Add the SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

# Register the RateLimitExceeded exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"message": "Too many requests. Please try again later."}
    )

# Initialize the Prometheus Instrumentator
instrumentator = Instrumentator()
# Instrument your FastAPI app
instrumentator.instrument(app).expose(app, "/metrics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to specific domains if needed)
    allow_credentials=True,  # Allows cookies to be sent across domains
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Include authentication api
app.include_router(auth.router,prefix=config.ROUTE_PREFIX, tags=["User Service"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI JWT Auth Prodigi1 Service"}

# Expose Prometheus metrics at '/metrics' endpoint
# This will be automatically handled by instrumentator
@app.get("/metrics")
async def metrics():
    # Prometheus metrics will be automatically exposed
    return JSONResponse(content={"message": "Metrics endpoint"})
