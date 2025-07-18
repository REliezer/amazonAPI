import uvicorn
import logging

from fastapi import FastAPI, Response, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from controllers.firebase import register_user_firebase, login_user_firebase
from controllers.productscatalog import get_products_catalog, create_product, get_products_by_category
from controllers.categories import get_category_name_by_id, get_count_products_by_category

from models.userregister import UserRegister
from models.userlogin import UserLogin
from models.productscatalog import ProductsCatalog

from utils.security import validateadmin
from utils.telemetry import setup_simple_telemetry, instrument_fastapi_app

logging.basicConfig( level=logging.INFO )
logger = logging.getLogger(__name__)
load_dotenv()

#telemetry_enabled = setup_simple_telemetry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    telemetry_enabled = await setup_simple_telemetry()
    if telemetry_enabled:
        instrument_fastapi_app(app)
        logger.info("Application Insights enabled")
        logger.info("FastAPI Instrumented")
    else:
        logger.warning("Application Insight disabled")
    
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Amazon API",
    description="Amazon API Lab expert system",
    version="0.0.3",
    lifespan=lifespan
)

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
async def create_new_product(request: Request, response: Response, product_data: ProductsCatalog) -> ProductsCatalog:
    cp = await create_product(product_data)
    return cp

@app.get("/products/")
async def get_products_by_category_id(category_id: int) -> list[ProductsCatalog]:
    products_by_category_id: list[ProductsCatalog] = await get_products_by_category(category_id)
    return products_by_category_id

#Otros endpoints
@app.get("/category/name/")
@validateadmin
async def get_category_name(request: Request, response: Response, category_id: int):
    category_name = await get_category_name_by_id(category_id)
    return category_name

@app.get("/category/count")
@validateadmin
async def get_count(request: Request, response: Response):
    return await get_count_products_by_category()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")