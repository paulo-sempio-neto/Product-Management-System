"""Explicit, transactional SQLite schema upgrades (run with python -m migrations)."""

import argparse
import re
import sqlite3
from typing import Literal

from persistence import DatabaseError

CURRENT_VERSION = 3
MAX_PRICE = "92233720368547758.07"
SchemaState = Literal["empty", "legacy", "revision_1", "revision_2", "current"]

LEGACY_SCHEMA = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL
)
"""

PRODUCTS_SCHEMA_V1 = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CONSTRAINT uq_products_name UNIQUE,
    price REAL NOT NULL,
    CONSTRAINT ck_products_name CHECK (
        typeof(name) = 'text' AND length(trim(name)) > 0
    ),
    CONSTRAINT ck_products_price CHECK (
        typeof(price) IN ('integer', 'real')
        AND price > 0 AND price <= 1.7976931348623157e308
    )
)
"""

PRODUCTS_SCHEMA_V2 = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CONSTRAINT uq_products_name UNIQUE,
    price_cents INTEGER NOT NULL,
    CONSTRAINT ck_products_name CHECK (
        typeof(name) = 'text' AND length(trim(name)) > 0
    ),
    CONSTRAINT ck_products_price_cents CHECK (
        typeof(price_cents) = 'integer'
        AND price_cents > 0
        AND price_cents <= 9223372036854775807
    )
)
"""

PRODUCTS_SCHEMA = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CONSTRAINT uq_products_name UNIQUE,
    price_cents INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT ck_products_name CHECK (
        typeof(name) = 'text' AND length(trim(name)) > 0
    ),
    CONSTRAINT ck_products_price_cents CHECK (
        typeof(price_cents) = 'integer'
        AND price_cents > 0
        AND price_cents <= 9223372036854775807
    ),
    CONSTRAINT ck_products_version CHECK (
        typeof(version) = 'integer'
        AND version > 0
    )
)
"""


class MigrationError(DatabaseError):
    """Storage requires an explicit upgrade or manual schema/data review."""


def _canonical(sql: str) -> tuple[str, ...]:
    """Compare known DDL tokens; quoted contents and token boundaries are exact.

    This is deliberately not a general SQL parser. Comments and unfamiliar DDL
    remain unrecognized. Only the optional creation clause and SQLite's quoted
    table name after RENAME are normalized, at their expected header positions.
    """
    tokens = re.findall(
        r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|"
        r"[A-Za-z_][A-Za-z_0-9]*|"
        r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|<=|>=|<>|!=|==|[^\s]",
        sql,
    )
    if tokens[:2] == ["CREATE", "TABLE"]:
        if tokens[2:5] == ["IF", "NOT", "EXISTS"]:
            del tokens[2:5]
        if tokens[2:3] == ['"products"']:
            tokens[2] = "products"
    if tokens[-1:] == [";"]:
        tokens.pop()
    return tuple(tokens)


def inspect_schema(connection: sqlite3.Connection) -> SchemaState:
    """Read schema metadata and validate legacy data without modifying storage."""
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    objects = connection.execute(
        "SELECT type, name, sql FROM sqlite_schema "
        "WHERE name NOT GLOB 'sqlite_*' ORDER BY name"
    ).fetchall()
    if version == 0 and not objects:
        return "empty"
    product_tables = [row for row in objects if row[:2] == ("table", "products")]
    if len(product_tables) != 1:
        raise MigrationError("Unknown schema; manual review required")
    sql = _canonical(product_tables[0][2])
    if version == CURRENT_VERSION and sql == _canonical(PRODUCTS_SCHEMA):
        return "current"
    # Rebuilding a table with unknown indexes, views, triggers or referencing
    # tables could lose behavior. Refuse rather than silently discarding them.
    if len(objects) != 1:
        raise MigrationError("Customized legacy schema; manual review required")
    if version == 2 and sql == _canonical(PRODUCTS_SCHEMA_V2):
        return "revision_2"
    if version == 1 and sql == _canonical(PRODUCTS_SCHEMA_V1):
        _validate_price_schema_rows(connection, "revision 3")
        return "revision_1"
    if version != 0 or sql != _canonical(LEGACY_SCHEMA):
        raise MigrationError("Unsupported schema/version; manual review required")
    _validate_price_schema_rows(connection, "revision 3")
    return "legacy"


def ensure_current(connection: sqlite3.Connection) -> None:
    if inspect_schema(connection) != "current":
        raise MigrationError("Schema upgrade required; run python -m migrations")


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Only brand-new databases may be initialized automatically at startup."""
    state = inspect_schema(connection)
    if state == "empty":
        connection.execute(PRODUCTS_SCHEMA)
        connection.execute(f"PRAGMA user_version = {CURRENT_VERSION}")
    elif state != "current":
        raise MigrationError("Schema upgrade required; run python -m migrations")


def upgrade_schema(connection: sqlite3.Connection) -> None:
    """Upgrade known product tables to revision 3, preserving rows and ID history.

    The caller owns one transaction spanning inspection, copy, and version stamp.
    Any exception must roll back the entire transaction. Stop application writers
    and back up the database before running this operator-only migration.
    """
    if not connection.in_transaction:
        raise MigrationError("Migration requires an enclosing transaction")
    state = inspect_schema(connection)
    if state == "current":
        return
    if state == "empty":
        initialize_schema(connection)
        return
    if state not in {"legacy", "revision_1", "revision_2"}:
        raise MigrationError("Unsupported schema/version; manual review required")
    sequence = connection.execute(
        "SELECT seq FROM sqlite_sequence WHERE name = 'products'"
    ).fetchone()
    connection.execute(
        PRODUCTS_SCHEMA.replace("CREATE TABLE products", "CREATE TABLE products_v3")
    )
    if state == "revision_2":
        connection.execute(
            "INSERT INTO products_v3(id, name, price_cents, version) "
            "SELECT id, name, price_cents, 1 FROM products"
        )
    else:
        connection.execute(
            "INSERT INTO products_v3(id, name, price_cents, version) "
            "SELECT id, name, CAST(round(price * 100) AS INTEGER), 1 FROM products"
        )
    connection.execute("DROP TABLE products")
    connection.execute("ALTER TABLE products_v3 RENAME TO products")
    if sequence is not None:
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'products'")
        connection.execute(
            "INSERT INTO sqlite_sequence(name, seq) VALUES ('products', ?)", sequence
        )
    connection.execute(f"PRAGMA user_version = {CURRENT_VERSION}")
    ensure_current(connection)


def _validate_price_schema_rows(
    connection: sqlite3.Connection, target_revision: str
) -> None:
    invalid = connection.execute(
        f"SELECT id FROM products WHERE "
        "typeof(name) != 'text' OR length(trim(name)) = 0 OR "
        "typeof(price) NOT IN ('integer', 'real') OR "
        f"NOT (price > 0 AND price <= {MAX_PRICE}) OR "
        "abs((price * 100) - round(price * 100)) > 0.000001 "
        "LIMIT 1"
    ).fetchone()
    if invalid is not None:
        raise MigrationError(
            f"Legacy data violates {target_revision}; manual repair required"
        )


def main() -> int:
    # Local import keeps SQLite connection lifecycle in the existing adapter.
    from database import get_connection

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "upgrade"))
    parser.add_argument("--database", required=True, help="Existing SQLite file path")
    args = parser.parse_args()
    try:
        with get_connection(
            args.database, read_only=args.command == "status", existing_only=True
        ) as connection:
            if args.command == "upgrade":
                upgrade_schema(connection)
            state = inspect_schema(connection)
        print(f"Schema: {state}; target revision: {CURRENT_VERSION}")
    except MigrationError as exc:
        print(f"Migration refused: {exc}")
        return 1
    except DatabaseError:
        # No product values, connection details or raw driver exceptions in output.
        print("Migration check failed; verify path, schema, data and permissions.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
