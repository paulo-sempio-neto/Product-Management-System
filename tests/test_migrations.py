import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from decimal import Decimal

import pytest

import database
import migrations
import product_service


@pytest.fixture
def legacy_db(tmp_path):
    target = str(tmp_path / "legacy.db")
    with database.get_connection(target) as connection:
        connection.execute(migrations.LEGACY_SCHEMA)
        connection.execute(
            "INSERT INTO products(id, name, price) VALUES (4, 'Precise', 1.23)"
        )
        connection.execute(
            "INSERT INTO products(id, name, price) VALUES (99, 'Deleted', 1)"
        )
        connection.execute("DELETE FROM products WHERE id = 99")
    return target


def snapshot(path):
    with database.get_connection(path, read_only=True) as connection:
        return list(connection.iterdump())


def test_fresh_database_is_versioned_and_initialization_is_idempotent(tmp_path):
    target = str(tmp_path / "fresh.db")
    database.create_table(target)
    database.create_product("Keep", 112, target)
    before = snapshot(target)
    database.create_table(target)
    assert snapshot(target) == before
    with database.get_connection(target, read_only=True) as connection:
        assert migrations.inspect_schema(connection) == "current"
        assert connection.execute("PRAGMA user_version").fetchone() == (2,)


def test_legacy_startup_and_health_refuse_without_writes(legacy_db):
    before = snapshot(legacy_db)
    with pytest.raises(product_service.ProductPersistenceError):
        product_service.initialize_products(legacy_db)
    with pytest.raises(database.DatabaseError):
        database.check_health(legacy_db)
    assert snapshot(legacy_db) == before


def test_explicit_upgrade_preserves_rows_and_deleted_id_history(legacy_db):
    with database.get_connection(legacy_db) as connection:
        migrations.upgrade_schema(connection)
    assert database.load_products(legacy_db) == [
        {"id": 4, "name": "Precise", "price": Decimal("1.23")}
    ]
    assert database.create_product("Next", 200, legacy_db) == 100
    current = snapshot(legacy_db)
    with database.get_connection(legacy_db) as connection:
        migrations.upgrade_schema(connection)
    assert snapshot(legacy_db) == current
    database.check_health(legacy_db)


@pytest.mark.parametrize("price", [0, -1, float("inf"), "not-numeric", 1.234])
def test_invalid_legacy_data_is_not_repaired_or_versioned(legacy_db, price):
    with database.get_connection(legacy_db) as connection:
        connection.execute("UPDATE products SET price = ?", (price,))
    before = snapshot(legacy_db)
    with pytest.raises(migrations.MigrationError, match="manual repair"):
        with database.get_connection(legacy_db) as connection:
            migrations.upgrade_schema(connection)
    assert snapshot(legacy_db) == before


@pytest.mark.parametrize(
    "customization",
    [
        "CREATE INDEX custom_name ON products(name)",
        "CREATE VIEW custom_view AS SELECT * FROM products",
        "CREATE TABLE extra(id INTEGER)",
        "CREATE INDEX sqliteXcustom ON products(name)",
        "ALTER TABLE products ADD COLUMN extra TEXT",
        "PRAGMA user_version = 42",
        "UPDATE products SET name = '   '",
        "CREATE TRIGGER custom_trigger AFTER INSERT ON products BEGIN SELECT 1; END",
    ],
)
def test_unrecognized_schema_or_data_is_refused(legacy_db, customization):
    with database.get_connection(legacy_db) as connection:
        connection.execute(customization)
    before = snapshot(legacy_db)
    with pytest.raises(migrations.MigrationError):
        with database.get_connection(legacy_db) as connection:
            migrations.upgrade_schema(connection)
    assert snapshot(legacy_db) == before


def test_failure_after_table_replacement_rolls_back_everything(legacy_db, monkeypatch):
    before = snapshot(legacy_db)

    def fail_final_validation(_connection):
        raise RuntimeError("simulated interruption")

    monkeypatch.setattr(migrations, "ensure_current", fail_final_validation)
    with pytest.raises(RuntimeError, match="simulated"):
        with database.get_connection(legacy_db) as connection:
            migrations.upgrade_schema(connection)
    assert snapshot(legacy_db) == before
    with database.get_connection(legacy_db) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (0,)


def test_migration_rejects_autocommit_connection(legacy_db):
    with closing(sqlite3.connect(legacy_db, autocommit=True)) as connection:
        with pytest.raises(migrations.MigrationError, match="transaction"):
            migrations.upgrade_schema(connection)


@pytest.mark.parametrize("legacy", [False, True])
def test_upgrade_empty_database_with_or_without_legacy_table(tmp_path, legacy):
    target = str(tmp_path / "empty.db")
    with database.get_connection(target) as connection:
        if legacy:
            connection.execute(migrations.LEGACY_SCHEMA)
    with database.get_connection(target) as connection:
        migrations.upgrade_schema(connection)
    database.check_health(target)
    assert database.load_products(target) == []
    assert database.create_product("First", 100, target) == 1


@pytest.mark.parametrize("command", ["status", "upgrade"])
def test_cli_does_not_create_missing_database(tmp_path, command):
    target = tmp_path / "typo.db"
    result = subprocess.run(
        [sys.executable, "-B", "-m", "migrations", command, "--database", str(target)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert not target.exists()
    assert str(target) not in result.stdout + result.stderr


def test_cli_status_and_upgrade(legacy_db):
    before = snapshot(legacy_db)
    environment = os.environ.copy()
    environment["APP_ENV"] = "production"
    environment["DB_NAME"] = legacy_db
    for command, expected in [("status", "legacy"), ("upgrade", "current")]:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "migrations",
                command,
                "--database",
                legacy_db,
            ],
            env=environment,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert expected in result.stdout
        if command == "status":
            assert snapshot(legacy_db) == before


@pytest.mark.parametrize("price_cents", [0, -1, float("inf"), float("nan"), "invalid"])
def test_price_constraint_rejects_direct_insert_and_update(setup_products, price_cents):
    before = database.load_products(setup_products)
    with pytest.raises(database.DatabaseIntegrityError):
        database.create_product("Invalid", price_cents, setup_products)
    with pytest.raises(database.DatabaseIntegrityError):
        database.update_product(1, "Invalid", price_cents, setup_products)
    assert database.load_products(setup_products) == before


@pytest.mark.parametrize("name", ["", "   ", b"binary"])
def test_name_constraint_rejects_invalid_storage(setup_products, name):
    with pytest.raises(database.DatabaseIntegrityError):
        database.create_product(name, 100, setup_products)


def test_exact_name_uniqueness_and_cent_prices_are_preserved(setup_products):
    for name in ("rice", "RICE", "Ríce"):
        product_id = database.create_product(name, 123, setup_products)
        assert database.find_product_by_id(product_id, setup_products)["price"] == (
            Decimal("1.23")
        )
    with pytest.raises(database.DatabaseDuplicateError):
        database.create_product("Rice", 100, setup_products)


def test_current_version_with_schema_drift_is_rejected(tmp_path):
    target = str(tmp_path / "drift.db")
    database.create_table(target)
    with database.get_connection(target) as connection:
        connection.execute("ALTER TABLE products ADD COLUMN unexpected TEXT")
    with pytest.raises(migrations.MigrationError):
        database.check_health(target)


@pytest.mark.parametrize(
    ("original", "changed"),
    [
        ("'text'", "'te xt'"),
        ("'integer'", "'inte\nger'"),
        ("9223372036854775807", "9223372036854775806"),
    ],
)
def test_schema_verification_preserves_whitespace_in_literals(
    tmp_path, original, changed
):
    target = str(tmp_path / "changed-check.db")
    with database.get_connection(target) as connection:
        connection.execute(migrations.PRODUCTS_SCHEMA.replace(original, changed))
        connection.execute("PRAGMA user_version = 2")
    before = snapshot(target)
    with pytest.raises(migrations.MigrationError):
        database.check_health(target)
    with pytest.raises(migrations.MigrationError):
        database.create_table(target)
    assert snapshot(target) == before


@pytest.mark.parametrize(
    "schema", [migrations.LEGACY_SCHEMA, migrations.PRODUCTS_SCHEMA_V1]
)
def test_known_old_schema_allows_external_whitespace_and_quoted_table_name(
    tmp_path, schema
):
    target = str(tmp_path / "formatted.db")
    formatted = schema.replace(
        "CREATE TABLE products", 'CREATE\nTABLE IF NOT EXISTS "products"'
    ).replace(",\n", ",\n\n\t")
    with database.get_connection(target) as connection:
        connection.execute(formatted)
        if schema == migrations.PRODUCTS_SCHEMA_V1:
            connection.execute("PRAGMA user_version = 1")
        migrations.upgrade_schema(connection)
    database.check_health(target)
    assert database.create_product("Unchanged", 123, target) == 1


def test_current_schema_allows_external_whitespace_and_quoted_table_name(tmp_path):
    target = str(tmp_path / "formatted-current.db")
    formatted = migrations.PRODUCTS_SCHEMA.replace(
        "CREATE TABLE products", 'CREATE\nTABLE IF NOT EXISTS "products"'
    ).replace(",\n", ",\n\n\t")
    with database.get_connection(target) as connection:
        connection.execute(formatted)
        connection.execute("PRAGMA user_version = 2")
        migrations.upgrade_schema(connection)
    database.check_health(target)
    assert database.create_product("Unchanged", 123, target) == 1


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("CHECK (name != 'a'' b')", "CHECK (name != 'a''b')"),
        ("CHECK (name != 'IF NOT EXISTS')", "CHECK (name != '')"),
        ("CHECK (name != '\"products\"')", "CHECK (name != 'products')"),
        (
            "CREATE TABLE products (price_cents INTEGER)",
            "CREATE TABLE products (price_centsINTEGER)",
        ),
    ],
)
def test_schema_comparison_does_not_rewrite_quoted_content_or_merge_tokens(left, right):
    assert migrations._canonical(left) != migrations._canonical(right)
