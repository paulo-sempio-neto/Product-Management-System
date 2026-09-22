import os
import subprocess
import sys

import pytest

import config
import database


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in (
        "APP_ENV",
        "DB_BACKEND",
        "DB_NAME",
        "SQLITE_TIMEOUT",
        "API_DOCS_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)


def test_development_defaults():
    settings = config.get_settings()
    assert settings.environment == "development"
    assert settings.database_backend == "sqlite"
    assert settings.database_path == "produtos.db"
    assert settings.sqlite_timeout == 5.0
    assert settings.docs_enabled is True


@pytest.mark.parametrize("environment", ["testing", "production"])
def test_non_development_requires_explicit_database(monkeypatch, environment):
    monkeypatch.setenv("APP_ENV", environment)
    with pytest.raises(ValueError, match="DB_NAME"):
        config.get_settings()


@pytest.mark.parametrize("environment", ["development", "testing", "production"])
def test_environment_settings(monkeypatch, tmp_path, environment):
    target = tmp_path / "configured.db"
    monkeypatch.setenv("APP_ENV", environment)
    monkeypatch.setenv("DB_NAME", str(target))
    monkeypatch.setenv("SQLITE_TIMEOUT", "0.25")
    settings = config.get_settings()
    assert settings.database_path == str(target)
    assert settings.sqlite_timeout == 0.25
    assert settings.docs_enabled is (environment != "production")
    assert not target.exists()


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("APP_ENV", "prodution"),
        ("DB_BACKEND", "postgresql"),
        ("DB_BACKEND", "mysql"),
        ("DB_BACKEND", "sqllite"),
        ("DB_BACKEND", ""),
        ("DB_NAME", ""),
        ("DB_NAME", "   "),
        ("DB_NAME", ":memory:"),
        ("DB_NAME", "postgresql://localhost/products"),
        ("DB_NAME", "file:products.db?mode=memory"),
        ("SQLITE_TIMEOUT", "0"),
        ("SQLITE_TIMEOUT", "-1"),
        ("SQLITE_TIMEOUT", "nan"),
        ("SQLITE_TIMEOUT", "inf"),
        ("SQLITE_TIMEOUT", "invalid"),
        ("SQLITE_TIMEOUT", "61"),
        ("API_DOCS_ENABLED", "invalid"),
    ],
)
def test_invalid_configuration_fails_fast(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        config.get_settings()


def test_cli_database_default_respects_environment(monkeypatch, tmp_path):
    target = tmp_path / "cli.db"
    monkeypatch.setenv("DB_NAME", str(target))
    database.create_table()
    database.create_product("Configured", 2.0)
    assert database.load_products() == [{"id": 1, "name": "Configured", "price": 2.0}]


@pytest.mark.parametrize("override", [None, "true"])
def test_production_api_docs_configuration_without_database_writes(
    monkeypatch, tmp_path, override
):
    target = tmp_path / "production.db"
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DB_NAME", str(target))
    if override:
        monkeypatch.setenv("API_DOCS_ENABLED", override)
    result = subprocess.run(
        [sys.executable, "-B", "-c", "import api; print(api.app.docs_url)"],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == ("/docs" if override else "None")
    assert not target.exists()
