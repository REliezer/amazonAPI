import json
import logging
#from typing import Optional

from fastapi import HTTPException

from utils.database import execute_query_json
from utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache

from controllers.categories import get_category_name_by_id

from models.productscatalog import ProductsCatalog

logger = logging.getLogger(__name__)

PRODUCTS_CACHE_KEY = "products:catalog:all"
CACHE_TTL = 1800

async def get_products_catalog() -> list[ProductsCatalog]:
    redis_client = get_redis_client()
    cached_data = get_from_cache( redis_client , PRODUCTS_CACHE_KEY )
    if cached_data:
        return [ProductsCatalog(**item) for item in cached_data]

    query = "select top 20000 * from amazon.products"
    result = await execute_query_json(query)
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code=404, detail="Products catalog not found")

    store_in_cache( redis_client , PRODUCTS_CACHE_KEY , dict , CACHE_TTL )
    return [ProductsCatalog(**item) for item in dict]

async def create_product( product_data: ProductsCatalog ) -> ProductsCatalog:
    insert_query = """
        insert into amazon.products(
            asin,
            title,
            imgUrl,
            productURL,
            stars,
            price,
            category_id
        ) values(
            ?, ?, ?, ?, ?, ?, ?
        )
    """

    params = [
        product_data.asin,
        product_data.title,
        product_data.imgUrl,
        product_data.productURL,
        product_data.stars,
        product_data.price,
        product_data.category_id
    ]

    insert_result = await execute_query_json( insert_query , params, needs_commit=True )

    created_object = ProductsCatalog(
        asin=product_data.asin,
        title=product_data.title,
        imgUrl=product_data.imgUrl,
        productURL=product_data.productURL,
        stars=product_data.stars,
        price=product_data.price,
        category_id=product_data.category_id
    )

    redis_client = get_redis_client()
    cache_deleted = delete_cache( redis_client, PRODUCTS_CACHE_KEY )

    #Obtener el nombre de la categoria del nuevo producto para eliminar tambien su cache
    category_name = await get_category_name_by_id(product_data.category_id)
    cache_key = f"products:catalog:{category_name}"

    cache_deleted = delete_cache( redis_client, cache_key )

    return created_object

async def get_products_by_category(category_id) -> list[ProductsCatalog]:
    #Obtener el nombre de la categoria
    category_name = await get_category_name_by_id(category_id)

    cache_key = f"products:catalog:{category_name}"
    redis_client = get_redis_client()
    cached_data_category = get_from_cache( redis_client , cache_key )
    if cached_data_category:
        return [ProductsCatalog(**item) for item in cached_data_category]

    query = "SELECT * FROM amazon.products WHERE category_id = ?"
    result = await execute_query_json(query, category_id)
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code=404, detail="Products catalog not found")

    store_in_cache( redis_client , cache_key , dict , CACHE_TTL )
    return [ProductsCatalog(**item) for item in dict]
