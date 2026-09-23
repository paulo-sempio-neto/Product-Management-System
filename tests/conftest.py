import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient

import api
from config import Settings
from database import create_product, create_table
from repositories import get_repository


@pytest.fixture
def setup_products(tmp_path):
    """
    Creates test products in a temporary database.
    """

    db_file = tmp_path / "test.db"

    db_name = str(db_file)

    create_table(db_name)

    create_product("Rice", 1200, db_name)
    create_product("Beans", 800, db_name)
    create_product("Pasta", 500, db_name)

    return db_name


@pytest.fixture
def api_db_path(tmp_path):
    return tmp_path / "api.db"


@pytest.fixture
def sqlite_repository(api_db_path):
    return get_repository(
        settings=Settings(environment="testing", database_path=str(api_db_path))
    )


@pytest.fixture(params=["sqlite"])
def product_repository(request):
    """Add backend fixtures here to reuse API and repository behavior tests."""
    return request.getfixturevalue(f"{request.param}_repository")


@pytest.fixture
def api_app(product_repository):
    return api.create_app(Settings(), repository=product_repository)


@pytest.fixture
def api_client(api_app):
    with TestClient(api_app) as client:
        yield client


@pytest.fixture
def sqlite_api_client(sqlite_repository):
    with TestClient(api.create_app(Settings(), repository=sqlite_repository)) as client:
        yield client


@pytest.fixture
def seeded_api_client(api_client):
    for product in (
        {"name": "Arroz", "price": 12.0},
        {"name": "Feijão", "price": 8.0},
        {"name": "Macarrão", "price": 5.0},
    ):
        response = api_client.post("/products", json=product)
        assert response.status_code == 201

    return api_client
