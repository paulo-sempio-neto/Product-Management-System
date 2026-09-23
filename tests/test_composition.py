from decimal import Decimal
from unittest.mock import create_autospec

import pytest
from fastapi.testclient import TestClient

import api
import config
import database
from persistence import ProductRepository
from repositories import SQLiteProductRepository, get_repository


def test_factory_construction_has_no_database_side_effects(tmp_path):
    target = tmp_path / "not-created.db"
    settings = config.Settings(database_path=str(target))
    storage = get_repository(settings=settings)
    assert isinstance(storage, SQLiteProductRepository)
    assert not target.exists()


def test_configured_repository_keeps_path_and_timeout(tmp_path, monkeypatch):
    target = tmp_path / "selected.db"
    settings = config.Settings(database_path=str(target), sqlite_timeout=0.125)
    storage = get_repository(settings=settings)
    monkeypatch.setenv("DB_BACKEND", "postgresql")
    monkeypatch.setenv("DB_NAME", str(tmp_path / "wrong.db"))
    monkeypatch.setenv("SQLITE_TIMEOUT", "invalid")
    storage.initialize()
    product_id = storage.create("First", 123)
    assert storage.get(product_id) == {
        "id": product_id,
        "name": "First",
        "price": Decimal("1.23"),
        "version": 1,
    }
    assert storage.find_by_name("First") == storage.get(product_id)
    assert storage.update(product_id, "Updated", 200, 1)
    assert len(storage.list_products()) == 1
    assert storage.list_products_page(limit=10, offset=0) == {
        "items": [
            {
                "id": product_id,
                "name": "Updated",
                "price": Decimal("2.00"),
                "version": 2,
            }
        ],
        "total": 1,
    }
    storage.check_health()
    assert storage.delete(product_id)
    with database.get_connection(settings=settings) as connection:
        assert connection.execute("PRAGMA busy_timeout").fetchone() == (125,)
    assert not (tmp_path / "wrong.db").exists()


@pytest.mark.parametrize("backend", ["postgresql", "mysql", "sqllite", ""])
def test_unsupported_backend_never_falls_back_to_sqlite(tmp_path, monkeypatch, backend):
    target = tmp_path / "must-not-exist.db"
    monkeypatch.setenv("DB_BACKEND", backend)
    monkeypatch.setenv("DB_NAME", str(target))
    with pytest.raises(ValueError):
        get_repository()
    with pytest.raises(ValueError):
        api.create_app()
    assert not target.exists()


def test_legacy_path_override_is_validated_and_works_in_production(
    tmp_path, monkeypatch
):
    target = tmp_path / "explicit.db"
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DB_BACKEND", "sqlite")
    monkeypatch.delenv("DB_NAME", raising=False)
    storage = get_repository(str(target))
    assert not target.exists()
    storage.initialize()
    assert target.exists()
    with pytest.raises(ValueError):
        get_repository(":memory:")


def test_factory_rejects_conflicting_configuration():
    with pytest.raises(ValueError, match="either"):
        get_repository("explicit.db", settings=config.Settings())


def test_application_uses_injected_storage_for_startup_and_requests(
    tmp_path, monkeypatch
):
    target = tmp_path / "unused.db"
    storage = create_autospec(ProductRepository, instance=True, spec_set=True)
    product = {"id": 42, "name": "Injected", "price": Decimal("2.00"), "version": 1}
    storage.list_products_page.return_value = {"items": [product], "total": 1}

    def forbid_default_storage(**_kwargs):
        pytest.fail("Explicit injection must not create the configured backend")

    monkeypatch.setattr(api, "get_repository", forbid_default_storage)
    application = api.create_app(
        config.Settings(database_path=str(target)), repository=storage
    )
    storage.initialize.assert_not_called()
    with TestClient(application) as client:
        storage.initialize.assert_called_once_with()
        assert client.get("/products").json() == {
            "items": [product],
            "page": 1,
            "limit": 20,
            "total": 1,
        }
        assert client.get("/health").json() == {"status": "ok"}
        storage.check_health.assert_called_once_with()
        assert client.get("/live").status_code == 200
        assert client.get("/").status_code == 200
    assert not target.exists()


def test_independent_applications_do_not_share_storage_or_docs(tmp_path):
    first_path = tmp_path / "first.db"
    second_path = tmp_path / "second.db"
    first_app = api.create_app(config.Settings(database_path=str(first_path)))
    second_app = api.create_app(
        config.Settings(database_path=str(second_path), docs_enabled=False)
    )
    assert not first_path.exists() and not second_path.exists()
    with TestClient(first_app) as first, TestClient(second_app) as second:
        assert (
            first.post("/products", json={"name": "Only first", "price": 1}).status_code
            == 201
        )
        assert len(first.get("/products").json()["items"]) == 1
        assert second.get("/products").json() == {
            "items": [],
            "page": 1,
            "limit": 20,
            "total": 0,
        }
        assert first.get("/openapi.json").status_code == 200
        assert second.get("/openapi.json").status_code == 404
