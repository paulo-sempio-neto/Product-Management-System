import pytest

from database import (
    create_table,
    save_products
)


@pytest.fixture
def setup_products():
    """
    Creates test products in the database.
    """

    create_table()

    products = [
        {
            "id": 1,
            "name": "Rice",
            "price": 12.0
        },
        {
            "id": 2,
            "name": "Beans",
            "price": 8.0
        },
        {
            "id": 3,
            "name": "Pasta",
            "price": 5.0
        }
    ]

    save_products(products)

    return products