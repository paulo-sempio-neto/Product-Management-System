"""Composition boundary: selects the existing SQLite adapter by default."""

from dataclasses import dataclass

import database
from config import Settings, get_settings
from persistence import DatabasePath, Product, ProductRepository


@dataclass(frozen=True)
class SQLiteProductRepository:
    database_path: DatabasePath = None
    settings: Settings | None = None

    def initialize(self) -> None:
        database.create_table(self.database_path, settings=self.settings)

    def check_health(self) -> None:
        database.check_health(self.database_path, settings=self.settings)

    def list_products(self) -> list[Product]:
        return database.load_products(self.database_path, settings=self.settings)

    def get(self, product_id: int) -> Product | None:
        return database.find_product_by_id(
            product_id, self.database_path, settings=self.settings
        )

    def find_by_name(self, name: str) -> Product | None:
        return database.find_product_by_name(
            name, self.database_path, settings=self.settings
        )

    def create(self, name: str, price: float) -> int:
        return database.create_product(
            name, price, self.database_path, settings=self.settings
        )

    def update(self, product_id: int, name: str, price: float) -> bool:
        return database.update_product(
            product_id, name, price, self.database_path, settings=self.settings
        )

    def delete(self, product_id: int) -> bool:
        return database.delete_product(
            product_id, self.database_path, settings=self.settings
        )


def get_repository(
    db_name: DatabasePath = None, *, settings: Settings | None = None
) -> ProductRepository:
    """Construct storage without I/O; never silently fall back to another backend."""
    if settings is not None and db_name is not None:
        raise ValueError("Pass either db_name or settings, not both")
    resolved = settings if settings is not None else get_settings(database_path=db_name)
    if resolved.database_backend == "sqlite":
        return SQLiteProductRepository(settings=resolved)
    raise ValueError("Unsupported database backend")
