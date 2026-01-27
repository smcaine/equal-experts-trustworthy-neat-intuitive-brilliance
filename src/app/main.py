"""
Application entrypoint and factory for the Gists FastAPI app.
"""

import logging

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import gists_router, healthchecker_router
from .settings import get_settings

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
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=get_settings().app.port)
