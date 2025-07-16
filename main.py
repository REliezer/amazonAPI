import uvicorn
import logging

from fastapi import FastAPI, Response, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from controllers.firebase import register_user_firebase, login_user_firebase
from controllers.productscatalog import get_products_catalog, create_serie

from models.userregister import UserRegister
from models.userlogin import UserLogin
from models.productscatalog import ProductsCatalog

from utils.security import validateadmin
from utils.telemetry import setup_simple_telemetry, instrument_fastapi_app

logging.basicConfig( level=logging.INFO )
logger = logging.getLogger(__name__)
load_dotenv()

telemetry_enabled = setup_simple_telemetry()
if telemetry_enabled:
    logger.info("Application Insights enabled")
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
else:
    logger.warning("Application Insight disabled")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Amazon API",
    description="Amazon API Lab expert system",
    version="0.0.3",
    lifespan=lifespan
)

if telemetry_enabled:
#    instrument_fastapi_app(app)
    FastAPIInstrumentor.instrument_app(app)
#    logger.info("Application Insights enabled")
    logger.info("FastAPI Instrumented")
#else:
#    logger.warning("Application Insight disabled")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
        , "version": "0.0.1"
    }

@app.get("/")
async def read_root(request: Request, response: Response):
    return {
        "hello": "world"
    }


@app.post("/signup")
async def signup(user: UserRegister):
    result = await register_user_firebase(user)
    return result


@app.post("/login")
async def login(user: UserLogin):
    result = await login_user_firebase(user)
    return result


@app.get("/products")
async def get_products() -> list[ProductsCatalog]:
    """Get all products from the catalog"""
    products: list[ProductsCatalog] = await get_products_catalog()
    return products

@app.post("/products", response_model=ProductsCatalog, status_code=201)
@validateadmin
async def create_new_series(request: Request, response: Response, series_data: ProductsCatalog) -> ProductsCatalog:
    cs = await create_serie(series_data)
    return cs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")