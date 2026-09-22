"""Explicit, transactional SQLite schema upgrades (run with python -m migrations)."""

import argparse
import sqlite3
from typing import Literal

from persistence import DatabaseError

CURRENT_VERSION = 1
SchemaState = Literal["empty", "legacy", "current"]

LEGACY_SCHEMA = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL
)
"""

# Preserve binary name equality and float precision. Currency/rounding semantics
# are deliberately not inferred from a field currently exposed as a JSON number.
PRODUCTS_SCHEMA = """
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


class MigrationError(DatabaseError):
    """Storage requires an explicit upgrade or manual schema/data review."""


def _canonical(sql: str) -> str:
    # Only recognize the project's known DDL, allowing whitespace and the quoting
    # introduced by SQLite's RENAME. Do not adopt arbitrary look-alike tables.
    return "".join(
        sql.replace('"products"', "products").replace("IF NOT EXISTS", "").split()
    ).rstrip(";")


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
    if version != 0 or sql != _canonical(LEGACY_SCHEMA):
        raise MigrationError("Unsupported schema/version; manual review required")
    # Rebuilding a table with unknown indexes, views, triggers or referencing
    # tables could lose behavior. Refuse rather than silently discarding them.
    if len(objects) != 1:
        raise MigrationError("Customized legacy schema; manual review required")
    invalid = connection.execute(
        "SELECT id FROM products WHERE "
        "typeof(name) != 'text' OR length(trim(name)) = 0 OR "
        "typeof(price) NOT IN ('integer', 'real') OR "
        "NOT (price > 0 AND price <= 1.7976931348623157e308) LIMIT 1"
    ).fetchone()
    if invalid is not None:
        raise MigrationError("Legacy data violates revision 1; manual repair required")
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
    """Revision 1: rebuild the known legacy table, preserving rows and ID history.

    The caller owns one transaction spanning inspection, copy, and version stamp.
    Any exception must roll back the entire transaction. Stop application writers
    and back up the database before running this operator-only migration.
    """
    if not connection.in_transaction:
        raise MigrationError("Migration requires an enclosing transaction")
    state = inspect_schema(connection)
    if state != "legacy":
        initialize_schema(connection)
        return
    sequence = connection.execute(
        "SELECT seq FROM sqlite_sequence WHERE name = 'products'"
    ).fetchone()
    connection.execute(
        PRODUCTS_SCHEMA.replace("CREATE TABLE products", "CREATE TABLE products_v1")
    )
    connection.execute(
        "INSERT INTO products_v1(id, name, price) SELECT id, name, price FROM products"
    )
    connection.execute("DROP TABLE products")
    connection.execute("ALTER TABLE products_v1 RENAME TO products")
    if sequence is not None:
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'products'")
        connection.execute(
            "INSERT INTO sqlite_sequence(name, seq) VALUES ('products', ?)", sequence
        )
    connection.execute(f"PRAGMA user_version = {CURRENT_VERSION}")
    ensure_current(connection)


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
