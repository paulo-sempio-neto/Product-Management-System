import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient

import api
from database import create_product, create_table


@pytest.fixture
def setup_products(tmp_path):
    """
    Creates test products in a temporary database.
    """

    db_file = tmp_path / "test.db"

    db_name = str(db_file)

    create_table(db_name)

    create_product("Rice", 12.0, db_name)
    create_product("Beans", 8.0, db_name)
    create_product("Pasta", 5.0, db_name)

    return db_name


@pytest.fixture
def api_db_path(tmp_path):
    return tmp_path / "api.db"


@pytest.fixture
def api_client(api_db_path, monkeypatch):
    monkeypatch.setattr(api, "DB_NAME", str(api_db_path))

    with TestClient(api.app) as client:
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
