"""Backend-neutral product records, failures, and repository contract."""

from typing import Protocol, TypedDict

DatabasePath = str | None


class Product(TypedDict):
    id: int
    name: str
    price: float


class DatabaseError(Exception):
    """A persistence operation could not be completed."""


class DatabaseIntegrityError(DatabaseError):
    """Stored data violates a constraint."""


class DatabaseDuplicateError(DatabaseIntegrityError):
    """The unique product-name constraint was violated."""


class ProductRepository(Protocol):
    """Adapters own SQL, connections, transactions, and driver error translation.

    Names use exact, case-sensitive uniqueness. Reads are ordered by ID.
    Writes commit before returning; update/delete return False for a missing ID.
    initialize must not silently upgrade existing storage. check_health is read-only.
    """

    def initialize(self) -> None: ...
    def check_health(self) -> None: ...
    def list_products(self) -> list[Product]: ...
    def get(self, product_id: int) -> Product | None: ...
    def find_by_name(self, name: str) -> Product | None: ...
    def create(self, name: str, price: float) -> int: ...
    def update(self, product_id: int, name: str, price: float) -> bool: ...
    def delete(self, product_id: int) -> bool: ...
