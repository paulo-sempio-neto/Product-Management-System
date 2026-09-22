import sqlite3

import pytest

import database
import product_service


def test_failed_bulk_replace_rolls_back_original_products(setup_products):
    before = database.load_products(setup_products)
    with pytest.raises(database.DatabaseDuplicateError):
        database.save_products(
            [
                {"id": 10, "name": "Duplicate", "price": 1.0},
                {"id": 11, "name": "Duplicate", "price": 2.0},
            ],
            setup_products,
        )
    assert database.load_products(setup_products) == before


def test_connection_rolls_back_non_sqlite_exception_and_closes(setup_products):
    with pytest.raises(RuntimeError, match="cancelled"):
        with database.get_connection(setup_products) as connection:
            connection.execute("DELETE FROM products")
            raise RuntimeError("cancelled")
    assert len(database.load_products(setup_products)) == 3
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")


def test_connection_commits_and_closes(setup_products):
    with database.get_connection(setup_products) as connection:
        connection.execute("UPDATE products SET price = 7 WHERE id = 1")
    assert database.find_product_by_id(1, setup_products)["price"] == 7
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")


def test_sqlite_errors_are_translated_and_connection_closed(setup_products):
    with pytest.raises(database.DatabaseError) as caught:
        with database.get_connection(setup_products) as connection:
            connection.execute("SELECT * FROM missing_table")
    assert isinstance(caught.value.__cause__, sqlite3.OperationalError)
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")


def test_lock_contention_is_bounded_and_translated(setup_products, monkeypatch):
    monkeypatch.setenv("SQLITE_TIMEOUT", "0.01")
    with database.get_connection(setup_products) as connection:
        connection.execute("UPDATE products SET price = 9 WHERE id = 1")
        with pytest.raises(database.DatabaseError):
            database.create_product("Blocked", 1.0, setup_products)
    assert database.find_product_by_name("Blocked", setup_products) is None


def test_non_unique_constraint_is_not_reported_as_duplicate(setup_products):
    with pytest.raises(database.DatabaseIntegrityError) as caught:
        with database.get_connection(setup_products) as connection:
            connection.execute("INSERT INTO products(name, price) VALUES(NULL, 2)")
    assert not isinstance(caught.value, database.DatabaseDuplicateError)


@pytest.mark.parametrize(
    ("database_error", "service_error"),
    [
        (database.DatabaseDuplicateError, product_service.DuplicateProductError),
        (database.DatabaseIntegrityError, product_service.ProductPersistenceError),
    ],
)
def test_service_classifies_write_failure(
    setup_products, monkeypatch, database_error, service_error
):
    def fail_write(*_args, **_kwargs):
        raise database_error("internal detail")

    monkeypatch.setattr(database, "create_product", fail_write)
    with pytest.raises(service_error):
        product_service.create_product("New", 1, setup_products)


@pytest.mark.parametrize("operation", ["update_product", "delete_product"])
def test_product_removed_between_lookup_and_write_is_not_success(
    setup_products, monkeypatch, operation
):
    monkeypatch.setattr(database, operation, lambda *_args, **_kwargs: False)
    with pytest.raises(product_service.ProductNotFoundError):
        if operation == "update_product":
            product_service.update_product(1, "Changed", 12, setup_products)
        else:
            product_service.delete_product(1, setup_products)


def test_health_does_not_create_missing_database(tmp_path):
    target = tmp_path / "missing.db"
    with pytest.raises(database.DatabaseError):
        database.check_health(str(target))
    assert not target.exists()


def test_out_of_range_ids_are_missing(setup_products):
    assert database.find_product_by_id(2**100, setup_products) is None


def test_huge_service_price_raises_validation_error():
    with pytest.raises(product_service.ProductValidationError):
        product_service.validate_price(10**400)
