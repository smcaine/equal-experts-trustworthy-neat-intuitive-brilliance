"""
Application entrypoint and factory for the Gists FastAPI app.
"""

import logging

import uvicorn
from aiocache import Cache, caches
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import gists_router, healthchecker_router
from .settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        A configured `FastAPI` instance with application routers included.
    """
    app = FastAPI(title="Gists FastAPI", version="0.1.0")
    app.include_router(gists_router)
    app.include_router(healthchecker_router)

    # Instrumentator: exposes `/metrics` and collects common FastAPI metrics.
    Instrumentator().instrument(app).expose(app)

    async def _init_cache() -> None:
        """Initialize FastAPICache on application startup.

        Uses the application's settings to decide whether to configure an
        aiocache Redis backend.
        """
        settings = get_settings()
        if not settings.app.redis_cache_enabled and not settings.app.redis_url:
            logger.info("Redis caching not enabled; skipping FastAPICache init")
            return

        prefix = settings.app.redis_users_namespace
        # if settings.app.redis_cache_enabled and settings.app.redis_url:
        # Configure aiocache to use Redis backend with the provided URL
        caches.set_config(
            {
                "default": {
                    "cache": "aiocache.RedisCache",
                    "endpoint": get_settings().app.redis_url,
                    "port": 6379,
                }
            }
        )

        FastAPICache.init(RedisBackend(Cache), prefix=prefix)
        logger.info("FastAPICache initialized with Redis backend")

    app.add_event_handler("startup", _init_cache)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=get_settings().app.port)
