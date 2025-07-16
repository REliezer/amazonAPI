import os
import json
import logging
import redis
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_CONNECTION_STRING")

def get_redis_client():
    if not REDIS_URL:
        logger.error("La variable de entorno REDIS_CONNECTION_STRING no está definida.")
        return None

    try:
        client = redis.from_url(
            REDIS_URL,
            decode_responses=True
        )

        client.ping()
        logger.info("Connected to Redis successfully using Connection String!")
        return client
    except Exception as e:
        # El error ahora será más específico si algo falla
        logger.error(f"Error connecting to Redis with Connection String: {e}")
        return None

def get_from_cache(redis_client, cache_key: str) -> Optional[Any]:
    if not redis_client:
        return None

    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info("✅ Cache hit for key: %s", cache_key)
            return json.loads(cached_data)
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ Corrupted cache data for key '{cache_key}', clearing: {str(e)}")
        redis_client.delete(cache_key)
    except Exception as e:
        logger.warning(f"⚠️ Cache retrieval failed for key '{cache_key}': {str(e)}")

    return None


def delete_cache(redis_client, cache_key: str) -> bool:
    if not redis_client:
        logger.info("ℹ️ Redis not available - cache deletion skipped")
        return False

    try:
        result = redis_client.delete(cache_key)
        if result:
            logger.info(f"🗑️ Cache key '{cache_key}' deleted successfully")
            return True
        else:
            logger.info(f"ℹ️ Cache key '{cache_key}' did not exist")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete cache key '{cache_key}': {str(e)}")
        return False


def store_in_cache(redis_client, cache_key: str, data: list[dict], expiration: int) -> None:
    if not redis_client:
        logger.info("Redis not available - running without cache")
        return

    try:
        json_data = json.dumps(data, default=str)  # Handle datetime objects
        redis_client.setex(cache_key, expiration, json_data)
        logger.info(f"✅ Series catalog cached for {expiration} seconds")
    except Exception as e:
        logger.warning(f"⚠️ Failed to cache series catalog: {str(e)}")