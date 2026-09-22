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

    @model_validator(mode="after")
    def validate_database_path(self) -> Self:
        if not self.database_path.strip() or self.database_path == ":memory:":
            raise ValueError("DB_NAME must be a non-empty file path")
        if "://" in self.database_path or self.database_path.startswith("file:"):
            raise ValueError("DB_NAME must be a SQLite file path, not a database URL")
        return self


def get_settings(*, database_path: str | None = None) -> Settings:
    """Read configuration, with an optional explicit legacy file-path override."""
    environment = os.getenv("APP_ENV", "development")
    if database_path is None:
        database_path = os.getenv("DB_NAME")
    if environment in {"testing", "production"} and database_path is None:
        raise ValueError("DB_NAME must be explicitly set for testing and production")
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
        }
    )
