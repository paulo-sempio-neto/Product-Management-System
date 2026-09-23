"""Validated environment configuration shared by the API and CLI."""

import os
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    environment: Literal["development", "testing", "production"] = "development"
    # Extend supported choices only when an adapter is actually implemented.
    database_backend: Literal["sqlite"] = "sqlite"
    database_path: str = "produtos.db"
    sqlite_timeout: float = Field(default=5.0, gt=0, le=60, allow_inf_nan=False)
    docs_enabled: bool = True
    cors_allowed_origins: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_database_path(self) -> Self:
        if not self.database_path.strip() or self.database_path == ":memory:":
            raise ValueError("DB_NAME must be a non-empty file path")
        if "://" in self.database_path or self.database_path.startswith("file:"):
            raise ValueError("DB_NAME must be a SQLite file path, not a database URL")
        return self

    @model_validator(mode="after")
    def validate_cors_allowed_origins(self) -> Self:
        for origin in self.cors_allowed_origins:
            if not origin.strip():
                raise ValueError("CORS_ALLOWED_ORIGINS must not contain empty origins")
            if origin != origin.strip():
                raise ValueError("CORS_ALLOWED_ORIGINS must contain trimmed origins")
            if self.environment == "production" and "*" in origin:
                raise ValueError("CORS_ALLOWED_ORIGINS must not use '*' in production")
        return self


def _parse_cors_allowed_origins(
    value: str | None, *, default: tuple[str, ...]
) -> tuple[str, ...]:
    if value is None:
        return default
    return tuple(origin.strip() for origin in value.split(",") if origin.strip())


def get_settings(*, database_path: str | None = None) -> Settings:
    """Read configuration, with an optional explicit legacy file-path override."""
    environment = os.getenv("APP_ENV", "development")
    if database_path is None:
        database_path = os.getenv("DB_NAME")
    if environment in {"testing", "production"} and database_path is None:
        raise ValueError("DB_NAME must be explicitly set for testing and production")
    default_cors_allowed_origins = (
        ("http://localhost:5173", "http://127.0.0.1:5173")
        if environment == "development"
        else ()
    )
    return Settings.model_validate(
        {
            "environment": environment,
            "database_backend": os.getenv("DB_BACKEND", "sqlite"),
            "database_path": database_path
            if database_path is not None
            else "produtos.db",
            "sqlite_timeout": os.getenv("SQLITE_TIMEOUT", "5"),
            "docs_enabled": os.getenv(
                "API_DOCS_ENABLED", "false" if environment == "production" else "true"
            ),
            "cors_allowed_origins": _parse_cors_allowed_origins(
                os.getenv("CORS_ALLOWED_ORIGINS"),
                default=default_cors_allowed_origins,
            ),
        }
    )
