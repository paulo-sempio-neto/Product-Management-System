import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

from fastapi.testclient import TestClient

import api


def test_importing_api_does_not_initialize_database(tmp_path):
    database_path = tmp_path / "import_only.db"
    project_root = Path(__file__).resolve().parent.parent
    environment = os.environ.copy()
    environment["DB_NAME"] = str(database_path)
    environment["PYTHONPATH"] = str(project_root)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    result = subprocess.run(
        [sys.executable, "-c", "import api"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not database_path.exists()


def test_application_lifespan_initializes_database(api_db_path, monkeypatch):
    monkeypatch.setattr(api, "DB_NAME", str(api_db_path))
    assert not api_db_path.exists()

    with TestClient(api.app):
        assert api_db_path.exists()
        with closing(sqlite3.connect(api_db_path)) as connection:
            table = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'products'
                """
            ).fetchone()

    assert table == ("products",)


def test_root(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API de Produtos!"}


def test_api_client_starts_with_empty_database(api_client):
    response = api_client.get("/products")
    assert response.status_code == 200
    assert response.json() == []


def test_list_products(seeded_api_client):
    response = seeded_api_client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["name"] == "Arroz"


def test_create_product(api_client):
    response = api_client.post(
        "/products",
        json={"name": "Banana", "price": 5.0},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Banana"
    assert response.json()["price"] == 5.0
    assert "id" in response.json()


def test_create_product_duplicate(api_client):
    api_client.post("/products", json={"name": "Banana", "price": 5.0})
    response = api_client.post(
        "/products",
        json={"name": "Banana", "price": 10.0},
    )
    assert response.status_code == 400
    assert "Produto já cadastrado" in response.text


def test_create_product_invalid_price(api_client):
    response = api_client.post(
        "/products",
        json={"name": "Teste", "price": -10.0},
    )
    assert response.status_code == 422


def test_create_product_empty_name(api_client):
    response = api_client.post(
        "/products",
        json={"name": "", "price": 10.0},
    )
    assert response.status_code == 422


def test_get_product_by_id(seeded_api_client):
    response = seeded_api_client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Arroz"
    assert response.json()["price"] == 12.0


def test_get_product_not_found(seeded_api_client):
    response = seeded_api_client.get("/products/999")
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text


def test_update_product(seeded_api_client):
    response = seeded_api_client.put(
        "/products/1",
        json={"name": "Arroz Integral", "price": 15.0},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Arroz Integral"
    assert response.json()["price"] == 15.0


def test_update_product_not_found(seeded_api_client):
    response = seeded_api_client.put(
        "/products/999",
        json={"name": "Teste", "price": 10.0},
    )
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text


def test_delete_product(seeded_api_client):
    response = seeded_api_client.delete("/products/1")
    assert response.status_code == 204
    response = seeded_api_client.get("/products/1")
    assert response.status_code == 404


def test_delete_product_not_found(seeded_api_client):
    response = seeded_api_client.delete("/products/999")
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text


def test_search_products(seeded_api_client):
    response = seeded_api_client.get("/products/search/?name=ar")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Arroz"
    assert response.json()[1]["name"] == "Macarrão"


def test_search_products_not_found(seeded_api_client):
    response = seeded_api_client.get("/products/search/?name=xyz")
    assert response.status_code == 404
    assert "Nenhum produto encontrado" in response.text
