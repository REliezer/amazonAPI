import json
#import logging
#from typing import Optional

from fastapi import HTTPException

from utils.database import execute_query_json
#from utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache
from models.productscatalog import ProductsCatalog

#logger = logging.getLogger(__name__)

#SERIES_CACHE_KEY = "series:catalog:all"
#CACHE_TTL = 1800

async def get_products_catalog() -> list[ProductsCatalog]:
#    redis_client = get_redis_client()
#    cached_data = get_from_cache( redis_client , SERIES_CACHE_KEY )
#    if cached_data:
#        return [ProductsCatalog(**item) for item in cached_data]
#
    query = "select top 8000 * from amazon.products"
#    query = "select * from amazon.products"
    result = await execute_query_json(query)
    dict = json.loads(result)
    if not dict:
        raise HTTPException(status_code=404, detail="Products catalog not found")

#    store_in_cache( redis_client , SERIES_CACHE_KEY , dict , CACHE_TTL )
    return [ProductsCatalog(**item) for item in dict]

async def create_serie( serie_data: ProductsCatalog ) -> ProductsCatalog:

    max_id_query = " select isnull( max(id) , 0 ) max_id from amazon.products "
    max_id_result = await execute_query_json(max_id_query)
    max_id_data = json.loads(max_id_result)
    if not max_id_data or len(max_id_data) == 0:
        raise HTTPException( status_code=500 , detail="Failed DB connection" )    

    current_max_id = max_id_data[0].get( 'max_id' , 0 )
    new_id = current_max_id + 1

    insert_query = """
        insert into amazon.products(
            id
            , name
            , original_name
            , overview
            , status
            , original_language
        ) values(
            ?, ?, ?, ?, ?, ?
        )
    """

    params = [
        new_id
        , serie_data.name
        , serie_data.original_name
        , serie_data.overview
        , serie_data.status
        , serie_data.original_language
    ]

    insert_result = await execute_query_json( insert_query , params, needs_commit=True )

    created_object = ProductsCatalog(
        id=new_id
        ,name = serie_data.name
        ,original_name = serie_data.original_name
        ,overview = serie_data.overview
        ,status = serie_data.status
        ,original_language = serie_data.original_language
    )

#    redis_client = get_redis_client()
#    cache_deleted = delete_cache( redis_client, SERIES_CACHE_KEY )

    return created_object


