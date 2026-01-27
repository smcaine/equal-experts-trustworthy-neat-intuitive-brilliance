import json
from functools import wraps

from aiocache import Cache
from fastapi import HTTPException

from .settings import get_settings


def cache_response(
    ttl: int = get_settings().app.redis_cache_ttl, namespace: str = "users"
):
    """
    Caching decorator for FastAPI endpoints.

    ttl: Time to live for the cache in seconds.
    namespace: Namespace for cache keys in Redis.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if get_settings().app.redis_cache_enabled is False:
                return await func(*args, **kwargs)
            username = (
                kwargs.get("username") or args[0]
            )  # Assuming the user ID is the first argument
            cache_key = f"{namespace}:user:{username}"

            cache = Cache.REDIS(
                endpoint=get_settings().app.redis_url, port=6379, namespace=namespace
            )

            # Try to retrieve data from cache
            cached_value = await cache.get(cache_key)
            if cached_value:
                return json.loads(cached_value)  # Return cached data

            # Call the actual function if cache is not hit
            response = await func(*args, **kwargs)

            try:
                # Store the response in Redis with a TTL
                await cache.set(cache_key, json.dumps(response), ttl=ttl)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error caching data: {e}")

            return response

        return wrapper

    return decorator
