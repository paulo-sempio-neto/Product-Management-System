"""Composition boundary: selects the existing SQLite adapter by default."""

from dataclasses import dataclass

import database
from persistence import DatabasePath, Product, ProductRepository


@dataclass(frozen=True)
class SQLiteProductRepository:
    database_path: DatabasePath = None

    def initialize(self) -> None:
        database.create_table(self.database_path)

    def check_health(self) -> None:
        database.check_health(self.database_path)

    def list_products(self) -> list[Product]:
        return database.load_products(self.database_path)

    def get(self, product_id: int) -> Product | None:
        return database.find_product_by_id(product_id, self.database_path)

    def find_by_name(self, name: str) -> Product | None:
        return database.find_product_by_name(name, self.database_path)

    def create(self, name: str, price: float) -> int:
        return database.create_product(name, price, self.database_path)

    def update(self, product_id: int, name: str, price: float) -> bool:
        return database.update_product(product_id, name, price, self.database_path)

    def delete(self, product_id: int) -> bool:
        return database.delete_product(product_id, self.database_path)


def get_repository(db_name: DatabasePath = None) -> ProductRepository:
    return SQLiteProductRepository(db_name)
