import logging

import httpx
from fastapi import HTTPException

from .settings import get_settings


def paginate_git_pages(client: httpx.Client, url: str):
    """Yield successive pages of a GitHub API resource as JSON.

    This generator requests the first page at `url` using the provided
    `httpx.Client`, validates the response via `handle_gist_error`, and
    then yields the parsed JSON for each page. If the response contains a
    `Link` header pointing to additional pages, those are followed and
    yielded until no `next` relation is present.

    Args:
        client: An instance of `httpx.Client` used to perform requests.
        url: The URL of the first GitHub API page to request.

    Yields:
        The parsed JSON body for each page (typically a list/dict from GitHub).

    Raises:
        HTTPException: Propagated from `handle_gist_error` for upstream errors.
    """
    first_page = client.get(url, headers=get_settings().app.github_header)
    handle_gist_error(first_page)

    yield first_page.json()

    next_page = first_page
    while get_next_git_page(next_page) is not None:
        try:
            next_page_url = next_page.links["next"]["url"]
            next_page = client.get(
                next_page_url, headers=get_settings().app.github_header
            )
            handle_gist_error(next_page)
            logging.debug("next page url: %s", next_page_url)
            yield next_page.json()
        except KeyError:
            logging.info("No more Github pages")
            break


def get_next_git_page(page):
    """Return the page object if it contains pagination `Link` headers.

    The helper inspects the response headers for a `link` header and
    returns the original `page` object when pagination is present, or
    `None` when there are no additional pages.

    Args:
        page: An `httpx.Response` instance representing a GitHub API response.

    Returns:
        The original `page` when a `link` header is present, otherwise `None`.
    """
    return page if page.headers.get("link") is not None else None


def handle_gist_error(response):
    """
    Normalize upstream GitHub errors into FastAPI HTTPExceptions.

    Args:
        response: An `httpx.Response` instance to validate.

    Raises:
        HTTPException: 404 for user-not-found, 502 for other upstream errors.
    """
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error {e}") from e
