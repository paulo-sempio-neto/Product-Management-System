import math
import unicodedata
from collections.abc import Callable, Sequence
from functools import wraps

import database

Product = database.Product
DatabasePath = database.DatabasePath


class ProductServiceError(Exception):
    """Base error for product operations."""


class ProductValidationError(ProductServiceError):
    """Raised when product data violates a business rule."""


class ProductNotFoundError(ProductServiceError):
    """Raised when a requested product does not exist."""


class DuplicateProductError(ProductServiceError):
    """Raised when another product already uses the requested name."""


class ProductPersistenceError(ProductServiceError):
    """Raised when product data cannot be read or persisted."""


def _translate_database_errors[**P, T](function: Callable[P, T]) -> Callable[P, T]:
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return function(*args, **kwargs)
        except database.DatabaseDuplicateError as exc:
            raise DuplicateProductError from exc
        except database.DatabaseError as exc:
            raise ProductPersistenceError from exc

    return wrapper


def normalize_product_name(name: str) -> str:
    """Trim a product name while preserving the user's casing."""
    if not isinstance(name, str):
        raise ProductValidationError("Product name must be text")

    normalized_name = name.strip()
    if not normalized_name:
        raise ProductValidationError("Product name cannot be empty")
    return normalized_name


def validate_price(price: object) -> float:
    """Return a valid finite positive price."""
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ProductValidationError("Product price must be a number")

    try:
        normalized_price = float(price)
    except OverflowError as exc:
        raise ProductValidationError("Product price must be finite") from exc
    if not math.isfinite(normalized_price) or normalized_price <= 0:
        raise ProductValidationError("Product price must be greater than zero")
    return normalized_price


@_translate_database_errors
def initialize_products(db_name: DatabasePath = None) -> None:
    database.create_table(db_name)


@_translate_database_errors
def check_product_storage(db_name: DatabasePath = None) -> None:
    database.check_health(db_name)


@_translate_database_errors
def create_product(
    name: str,
    price: object,
    db_name: DatabasePath = None,
) -> Product:
    normalized_name = normalize_product_name(name)
    normalized_price = validate_price(price)

    if database.find_product_by_name(normalized_name, db_name) is not None:
        raise DuplicateProductError

    product_id = database.create_product(
        normalized_name,
        normalized_price,
        db_name,
    )
    return {
        "id": product_id,
        "name": normalized_name,
        "price": normalized_price,
    }


@_translate_database_errors
def list_products(db_name: DatabasePath = None) -> list[Product]:
    return database.load_products(db_name)


@_translate_database_errors
def get_product(product_id: int, db_name: DatabasePath = None) -> Product:
    product = database.find_product_by_id(product_id, db_name)
    if product is None:
        raise ProductNotFoundError
    return product


@_translate_database_errors
def update_product(
    product_id: int,
    name: str,
    price: object,
    db_name: DatabasePath = None,
) -> Product:
    get_product(product_id, db_name)
    normalized_name = normalize_product_name(name)
    normalized_price = validate_price(price)

    product_with_same_name = database.find_product_by_name(normalized_name, db_name)
    if (
        product_with_same_name is not None
        and product_with_same_name["id"] != product_id
    ):
        raise DuplicateProductError

    updated = database.update_product(
        product_id,
        normalized_name,
        normalized_price,
        db_name,
    )
    if not updated:
        raise ProductNotFoundError
    return {
        "id": product_id,
        "name": normalized_name,
        "price": normalized_price,
    }


@_translate_database_errors
def delete_product(
    product_id: int,
    db_name: DatabasePath = None,
) -> Product:
    product = get_product(product_id, db_name)
    if not database.delete_product(product_id, db_name):
        raise ProductNotFoundError
    return product


@_translate_database_errors
def search_products(
    partial_name: str,
    db_name: DatabasePath = None,
) -> list[Product]:
    normalized_partial_name = _normalize_for_search(partial_name)
    products = database.load_products(db_name)
    return [
        product
        for product in products
        if normalized_partial_name in _normalize_for_search(product["name"])
    ]


def calculate_average_price(products: Sequence[Product]) -> float:
    if not products:
        raise ProductNotFoundError
    return sum(product["price"] for product in products) / len(products)


def filter_products_by_minimum_price(
    products: Sequence[Product],
    minimum_price: object,
) -> list[Product]:
    normalized_price = validate_price(minimum_price)
    return [product for product in products if product["price"] >= normalized_price]


def _normalize_for_search(value: str) -> str:
    return (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
