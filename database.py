import sqlite3
import unicodedata
from collections.abc import Iterator
from contextlib import closing, contextmanager
from decimal import Decimal
from pathlib import Path
from typing import cast

from config import Settings, get_settings
from migrations import ensure_current, initialize_schema
from persistence import DatabaseDuplicateError as DatabaseDuplicateError
from persistence import DatabaseError as DatabaseError
from persistence import DatabaseIntegrityError as DatabaseIntegrityError
from persistence import DatabasePath as DatabasePath
from persistence import Product as Product
from persistence import ProductPage as ProductPage


@contextmanager
def get_connection(
    db_name: DatabasePath = None,
    *,
    read_only: bool = False,
    existing_only: bool = False,
    settings: Settings | None = None,
) -> Iterator[sqlite3.Connection]:
    """Yield a connection that is always committed/rolled back and closed."""
    settings = settings if settings is not None else get_settings(database_path=db_name)
    if settings.database_backend != "sqlite":
        raise ValueError("SQLite adapter requires the sqlite backend")
    database = db_name if db_name is not None else settings.database_path
    use_uri = read_only or existing_only
    if use_uri:
        mode = "ro" if read_only else "rw"
        database = Path(database).resolve().as_uri() + f"?mode={mode}"

    try:
        with closing(
            sqlite3.connect(
                database,
                timeout=settings.sqlite_timeout,
                autocommit=False,
                uri=use_uri,
            )
        ) as connection:
            connection.create_function(
                "normalize_for_search", 1, _normalize_for_search, deterministic=True
            )
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


def check_health(
    db_name: DatabasePath = None, *, settings: Settings | None = None
) -> None:
    """Probe the products table without creating a missing database."""
    with get_connection(db_name, read_only=True, settings=settings) as connection:
        ensure_current(connection)
        connection.execute("SELECT id FROM products LIMIT 1").fetchone()


PRICE_QUANTUM = Decimal("0.01")


def _price_from_cents(price_cents: int) -> Decimal:
    return (Decimal(price_cents) / 100).quantize(PRICE_QUANTUM)


def _price_to_cents(price: Decimal) -> int:
    cents = price * 100
    if cents != cents.to_integral_value():
        raise DatabaseIntegrityError("Product price must be stored as cents")
    return int(cents)


def _product_from_row(row: tuple[int, str, int]) -> Product:
    return {
        "id": row[0],
        "name": row[1],
        "price": _price_from_cents(row[2]),
    }


def create_table(
    db_name: DatabasePath = None, *, settings: Settings | None = None
) -> None:
    """Initialize empty storage; require explicit upgrades for existing schemas."""
    with get_connection(db_name, settings=settings) as connection:
        initialize_schema(connection)


def create_product(
    name: str,
    price_cents: int,
    db_name: DatabasePath = None,
    *,
    settings: Settings | None = None,
) -> int:
    """Insert a product and return its generated ID."""
    with get_connection(db_name, settings=settings) as connection:
        cursor = connection.execute(
            """
            INSERT INTO products (name, price_cents)
            VALUES (?, ?)
            """,
            (name, price_cents),
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
    price_cents: int,
    db_name: DatabasePath = None,
    *,
    settings: Settings | None = None,
) -> bool:
    """Update an existing product."""
    with get_connection(db_name, settings=settings) as connection:
        cursor = connection.execute(
            """
            UPDATE products
            SET name = ?, price_cents = ?
            WHERE id = ?
            """,
            (name, price_cents, product_id),
        )
        return cursor.rowcount == 1


def delete_product(
    product_id: int,
    db_name: DatabasePath = None,
    *,
    settings: Settings | None = None,
) -> bool:
    """Delete a product by ID."""
    with get_connection(db_name, settings=settings) as connection:
        cursor = connection.execute(
            """
            DELETE FROM products
            WHERE id = ?
            """,
            (product_id,),
        )
        return cursor.rowcount == 1


def load_products(
    db_name: DatabasePath = None, *, settings: Settings | None = None
) -> list[Product]:
    """Return all products in deterministic ID order."""
    with get_connection(db_name, settings=settings) as connection:
        rows = connection.execute(
            "SELECT id, name, price_cents FROM products ORDER BY id"
        ).fetchall()
    return [_product_from_row(row) for row in rows]


def load_products_page(
    *,
    limit: int,
    offset: int,
    name_filter: str | None = None,
    db_name: DatabasePath = None,
    settings: Settings | None = None,
) -> ProductPage:
    """Return one deterministic page and total count using SQL limits."""
    where_clause = ""
    parameters: list[object] = []
    if name_filter is not None:
        where_clause = "WHERE normalize_for_search(name) LIKE ?"
        parameters.append(f"%{_normalize_for_search(name_filter)}%")

    with get_connection(db_name, settings=settings) as connection:
        total = cast(
            int,
            connection.execute(
                f"SELECT COUNT(*) FROM products {where_clause}",
                parameters,
            ).fetchone()[0],
        )
        rows = connection.execute(
            f"""
            SELECT id, name, price_cents
            FROM products
            {where_clause}
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            [*parameters, limit, offset],
        ).fetchall()
    return {"items": [_product_from_row(row) for row in rows], "total": total}


def save_products(products: list[Product], db_name: DatabasePath = None) -> None:
    """Replace every stored product with the supplied product list."""
    with get_connection(db_name) as connection:
        connection.execute("DELETE FROM products")
        connection.executemany(
            "INSERT INTO products (id, name, price_cents) VALUES (?, ?, ?)",
            [
                (product["id"], product["name"], _price_to_cents(product["price"]))
                for product in products
            ],
        )


def find_product_by_id(
    product_id: int,
    db_name: DatabasePath = None,
    *,
    settings: Settings | None = None,
) -> Product | None:
    """Find a product by ID."""
    if not -(2**63) <= product_id < 2**63:
        return None
    with get_connection(db_name, settings=settings) as connection:
        row = connection.execute(
            "SELECT id, name, price_cents FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
    return None if row is None else _product_from_row(row)


def find_product_by_name(
    name: str,
    db_name: DatabasePath = None,
    *,
    settings: Settings | None = None,
) -> Product | None:
    """Find a product by its exact stored name."""
    with get_connection(db_name, settings=settings) as connection:
        row = connection.execute(
            "SELECT id, name, price_cents FROM products WHERE name = ?",
            (name,),
        ).fetchone()
    return None if row is None else _product_from_row(row)


def _normalize_for_search(value: str) -> str:
    return (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
