import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import TypedDict, cast

from config import get_settings

DatabasePath = str | None


class Product(TypedDict):
    """A product record as returned by the database layer."""

    id: int
    name: str
    price: float


class DatabaseError(Exception):
    """Base error raised when a database operation cannot be completed."""


class DatabaseIntegrityError(DatabaseError):
    """Raised when SQLite rejects data because of an integrity constraint."""


class DatabaseDuplicateError(DatabaseIntegrityError):
    """The unique product-name constraint was violated."""


@contextmanager
def get_connection(
    db_name: DatabasePath = None, *, read_only: bool = False
) -> Iterator[sqlite3.Connection]:
    """Yield a connection that is always committed/rolled back and closed."""
    settings = get_settings()
    database = db_name if db_name is not None else settings.database_path
    if read_only:
        database = Path(database).resolve().as_uri() + "?mode=ro"

    try:
        with closing(
            sqlite3.connect(
                database,
                timeout=settings.sqlite_timeout,
                autocommit=False,
                uri=read_only,
            )
        ) as connection:
            # SQLite's context manager commits on success and rolls back on
            # any exception, including non-SQLite exceptions. closing owns cleanup.
            with connection:
                yield connection
    except sqlite3.IntegrityError as exc:
        if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise DatabaseDuplicateError("Product name already exists") from exc
        raise DatabaseIntegrityError("Database integrity constraint failed") from exc
    except sqlite3.Error as exc:
        raise DatabaseError("Database operation failed") from exc


def check_health(db_name: DatabasePath = None) -> None:
    """Probe the products table without creating a missing database."""
    with get_connection(db_name, read_only=True) as connection:
        connection.execute("SELECT id FROM products LIMIT 1").fetchone()


def _product_from_row(row: tuple[int, str, float]) -> Product:
    return {
        "id": row[0],
        "name": row[1],
        "price": row[2],
    }


def create_table(db_name: DatabasePath = None) -> None:
    """Create the products table if it does not exist."""
    with get_connection(db_name) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL
            )
            """
        )


def create_product(name: str, price: float, db_name: DatabasePath = None) -> int:
    """Insert a product and return its generated ID."""
    with get_connection(db_name) as connection:
        cursor = connection.execute(
            """
            INSERT INTO products (name, price)
            VALUES (?, ?)
            """,
            (name, price),
        )
        return cast(int, cursor.lastrowid)


def clear_products(db_name: DatabasePath = None) -> None:
    """Remove all products and reset the autoincrement sequence."""
    with get_connection(db_name) as connection:
        connection.execute("DELETE FROM products")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'products'")


def update_product(
    product_id: int,
    name: str,
    price: float,
    db_name: DatabasePath = None,
) -> bool:
    """Update an existing product."""
    with get_connection(db_name) as connection:
        cursor = connection.execute(
            """
            UPDATE products
            SET name = ?, price = ?
            WHERE id = ?
            """,
            (name, price, product_id),
        )
        return cursor.rowcount == 1


def delete_product(product_id: int, db_name: DatabasePath = None) -> bool:
    """Delete a product by ID."""
    with get_connection(db_name) as connection:
        cursor = connection.execute(
            """
            DELETE FROM products
            WHERE id = ?
            """,
            (product_id,),
        )
        return cursor.rowcount == 1


def load_products(db_name: DatabasePath = None) -> list[Product]:
    """Return all products in deterministic ID order."""
    with get_connection(db_name) as connection:
        rows = connection.execute(
            "SELECT id, name, price FROM products ORDER BY id"
        ).fetchall()
    return [_product_from_row(row) for row in rows]


def save_products(products: list[Product], db_name: DatabasePath = None) -> None:
    """Replace every stored product with the supplied product list."""
    with get_connection(db_name) as connection:
        connection.execute("DELETE FROM products")
        connection.executemany(
            "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
            [
                (product["id"], product["name"], product["price"])
                for product in products
            ],
        )


def find_product_by_id(
    product_id: int,
    db_name: DatabasePath = None,
) -> Product | None:
    """Find a product by ID."""
    if not -(2**63) <= product_id < 2**63:
        return None
    with get_connection(db_name) as connection:
        row = connection.execute(
            "SELECT id, name, price FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
    return None if row is None else _product_from_row(row)


def find_product_by_name(
    name: str,
    db_name: DatabasePath = None,
) -> Product | None:
    """Find a product by its exact stored name."""
    with get_connection(db_name) as connection:
        row = connection.execute(
            "SELECT id, name, price FROM products WHERE name = ?",
            (name,),
        ).fetchone()
    return None if row is None else _product_from_row(row)
