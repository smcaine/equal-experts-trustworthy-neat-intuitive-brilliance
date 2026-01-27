"""Application settings and configuration models.

This module defines the nested application configuration model
(`CoreSettingsModel`), the top-level `Settings` container which reads
configuration from the environment (and `.env`), and a cached
`get_settings()` accessor for use across the application.
"""

from functools import cache
from typing import Optional

from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettingsModel(BaseModel):
    """Core application configuration values.

    Attributes:
        name: Human readable name for the application.
        redis_cache_enabled: Whether Redis caching is enabled.
        redis_cache_ttl: Default TTL for cached entries (seconds).
        redis_url: Optional Redis connection URL.
        redis_users_namespace: Namespace prefix for user-cache keys.
        port: Port the application should listen on.
        github_token: Optional GitHub personal access token for authenticated requests.
        max_per_page: Max items per page when requesting the GitHub API.
    """

    name: str = Field(default="Gists FastAPI Application")
    redis_cache_enabled: bool = Field(default=False)
    redis_cache_ttl: int = Field(default=300)
    redis_url: Optional[str] = Field(default=None)
    redis_users_namespace: str = Field(default="users")
    port: int = Field(default=8080)
    github_token: Optional[str] = Field(default=None)
    max_per_page: int = Field(default=100)

    @computed_field
    def github_header(self) -> dict:
        """Return HTTP headers suitable for GitHub API requests.

        If a `github_token` is configured, the Authorization header will be
        included. The Accept header for the GitHub v3 API is always set.

        Returns:
            A dict of headers to send with GitHub API requests.
        """
        if self.github_token:
            return {
                "authorization": "token {0}".format(self.github_token),
                "ACCEPT": "application/vnd.github.v3+json",
            }
        else:
            return {"ACCEPT": "application/vnd.github.v3+json"}


class Settings(BaseSettings):
    """Top-level settings container loaded from environment or `.env`.

    The `app` attribute contains an instance of `CoreSettingsModel` with
    application-specific configuration.

    Configuration details (env file, nested delimiter) are provided via
    `model_config` so environment variables like `APP__MAX_PER_PAGE` map
    correctly to nested fields.
    """

    model_config = SettingsConfigDict(
        env_ignore_empty=False,
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    app: CoreSettingsModel


@cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance.

    This function uses `functools.cache` to ensure that settings are parsed
    only once and the same `Settings` object is reused across the process.

    Returns:
        A `Settings` instance populated from the environment/.env file.
    """
    return Settings()
