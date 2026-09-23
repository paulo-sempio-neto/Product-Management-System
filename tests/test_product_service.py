from decimal import Decimal

import pytest

import database
import product_service


@pytest.fixture
def service_db(tmp_path):
    db_name = str(tmp_path / "service.db")
    product_service.initialize_products(db_name)
    return db_name


def test_create_product_normalizes_name_and_persists_product(service_db):
    product = product_service.create_product("  Mixed Case  ", 12, service_db)

    assert product == {"id": 1, "name": "Mixed Case", "price": Decimal("12.00")}
    assert product_service.get_product(1, service_db) == product


@pytest.mark.parametrize("name", ["", "   "])
def test_create_product_rejects_empty_name(service_db, name):
    with pytest.raises(product_service.ProductValidationError):
        product_service.create_product(name, 10.0, service_db)


@pytest.mark.parametrize("price", [0, -1, float("inf"), float("nan"), "1.234"])
def test_create_product_rejects_invalid_price(service_db, price):
    with pytest.raises(product_service.ProductValidationError):
        product_service.create_product("Produto", price, service_db)


def test_create_product_rejects_duplicate_name(service_db):
    product_service.create_product("Produto", 10.0, service_db)

    with pytest.raises(product_service.DuplicateProductError):
        product_service.create_product(" Produto ", 20.0, service_db)


def test_get_product_reports_missing_product(service_db):
    with pytest.raises(product_service.ProductNotFoundError):
        product_service.get_product(999, service_db)


def test_update_product_applies_shared_rules(service_db):
    product = product_service.create_product("Original", 10.0, service_db)

    updated = product_service.update_product(
        product["id"],
        "  Updated  ",
        15.0,
        service_db,
    )

    assert updated == {"id": 1, "name": "Updated", "price": Decimal("15.00")}
    assert product_service.get_product(1, service_db) == updated


def test_update_product_rejects_another_products_name(service_db):
    first = product_service.create_product("First", 10.0, service_db)
    second = product_service.create_product("Second", 20.0, service_db)

    with pytest.raises(product_service.DuplicateProductError):
        product_service.update_product(
            second["id"],
            first["name"],
            30.0,
            service_db,
        )


def test_update_and_delete_report_missing_product(service_db):
    with pytest.raises(product_service.ProductNotFoundError):
        product_service.update_product(999, "Missing", 10.0, service_db)

    with pytest.raises(product_service.ProductNotFoundError):
        product_service.delete_product(999, service_db)


def test_delete_product_returns_deleted_product(service_db):
    product = product_service.create_product("Produto", 10.0, service_db)

    deleted = product_service.delete_product(product["id"], service_db)

    assert deleted == product
    with pytest.raises(product_service.ProductNotFoundError):
        product_service.get_product(product["id"], service_db)


def test_search_products_ignores_case_and_accents(service_db):
    product_service.create_product("Feijão", 8.0, service_db)

    assert product_service.search_products("FEIJAO", service_db) == [
        {"id": 1, "name": "Feijão", "price": Decimal("8.00")}
    ]


def test_database_errors_are_translated(monkeypatch):
    def fail_to_load(_db_name, **_kwargs):
        raise database.DatabaseError("unavailable")

    monkeypatch.setattr(database, "load_products", fail_to_load)

    with pytest.raises(product_service.ProductPersistenceError):
        product_service.list_products("unavailable.db")


def test_price_reports_use_shared_validation():
    products = [
        {"id": 1, "name": "A", "price": Decimal("10.00")},
        {"id": 2, "name": "B", "price": Decimal("20.00")},
    ]

    assert product_service.calculate_average_price(products) == Decimal("15.00")
    assert product_service.filter_products_by_minimum_price(products, 15.0) == [
        products[1]
    ]
