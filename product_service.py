import math
import unicodedata
from collections.abc import Callable, Sequence
from functools import wraps

from persistence import (
    DatabaseDuplicateError,
    DatabaseError,
    DatabasePath,
    ProductRepository,
)
from persistence import Product as Product
from repositories import get_repository


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
        except DatabaseDuplicateError as exc:
            raise DuplicateProductError from exc
        except DatabaseError as exc:
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
def initialize_products(
    db_name: DatabasePath = None, *, repository: ProductRepository | None = None
) -> None:
    _repository(db_name, repository).initialize()


@_translate_database_errors
def check_product_storage(
    db_name: DatabasePath = None, *, repository: ProductRepository | None = None
) -> None:
    _repository(db_name, repository).check_health()


@_translate_database_errors
def create_product(
    name: str,
    price: object,
    db_name: DatabasePath = None,
    *,
    repository: ProductRepository | None = None,
) -> Product:
    normalized_name = normalize_product_name(name)
    normalized_price = validate_price(price)

    storage = _repository(db_name, repository)
    if storage.find_by_name(normalized_name) is not None:
        raise DuplicateProductError

    product_id = storage.create(
        normalized_name,
        normalized_price,
    )
    return {
        "id": product_id,
        "name": normalized_name,
        "price": normalized_price,
    }


@_translate_database_errors
def list_products(
    db_name: DatabasePath = None, *, repository: ProductRepository | None = None
) -> list[Product]:
    return _repository(db_name, repository).list_products()


@_translate_database_errors
def get_product(
    product_id: int,
    db_name: DatabasePath = None,
    *,
    repository: ProductRepository | None = None,
) -> Product:
    product = _repository(db_name, repository).get(product_id)
    if product is None:
        raise ProductNotFoundError
    return product


@_translate_database_errors
def update_product(
    product_id: int,
    name: str,
    price: object,
    db_name: DatabasePath = None,
    *,
    repository: ProductRepository | None = None,
) -> Product:
    storage = _repository(db_name, repository)
    get_product(product_id, repository=storage)
    normalized_name = normalize_product_name(name)
    normalized_price = validate_price(price)

    product_with_same_name = storage.find_by_name(normalized_name)
    if (
        product_with_same_name is not None
        and product_with_same_name["id"] != product_id
    ):
        raise DuplicateProductError

    updated = storage.update(
        product_id,
        normalized_name,
        normalized_price,
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
    *,
    repository: ProductRepository | None = None,
) -> Product:
    storage = _repository(db_name, repository)
    product = get_product(product_id, repository=storage)
    if not storage.delete(product_id):
        raise ProductNotFoundError
    return product


@_translate_database_errors
def search_products(
    partial_name: str,
    db_name: DatabasePath = None,
    *,
    repository: ProductRepository | None = None,
) -> list[Product]:
    normalized_partial_name = _normalize_for_search(partial_name)
    products = _repository(db_name, repository).list_products()
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


def _repository(
    db_name: DatabasePath, repository: ProductRepository | None
) -> ProductRepository:
    if repository is not None:
        if db_name is not None:
            raise ValueError("Pass either db_name or repository, not both")
        return repository
    return get_repository(db_name)


def _normalize_for_search(value: str) -> str:
    return (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
