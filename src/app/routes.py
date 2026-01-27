import logging

import httpx
from fastapi import APIRouter

from .cache import cache_response
from .settings import get_settings
from .utils import paginate_git_pages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.routes")
GITHUB_API_URL = "https://api.github.com"

gists_router = APIRouter()
healthchecker_router = APIRouter()


@gists_router.get("/users/{username}")
@cache_response(
    ttl=get_settings().app.redis_cache_ttl,
    namespace=get_settings().app.redis_users_namespace,
)
async def read_user_gists(username: str):
    """Return a paginated list of public gists for `username`.

    Args:
        username: GitHub username whose public gists will be returned.

    Returns:
        A dict with a single key `results` containing a list of gist pages.

    Raises:
        HTTPException: If the upstream GitHub API returns a 404 (user not found)
                       or an upstream error is encountered.
    """

    url = f"{GITHUB_API_URL}/users/{username}/gists?per_page={get_settings().app.max_per_page}"  # noqa: E501
    pages = []
    logger.info(f"Fetching gists for user: {username}")
    for page in paginate_git_pages(httpx.Client(), url):
        pages.append(page)
    return {"results": pages}


@healthchecker_router.get("/healthz")
async def health_check():
    return {"status": "ok"}
