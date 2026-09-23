import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

from fastapi.testclient import TestClient

import api
from config import Settings


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


def test_application_lifespan_initializes_database(api_db_path):
    application = api.create_app(Settings(database_path=str(api_db_path)))
    assert not api_db_path.exists()

    with TestClient(application):
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


def test_application_allows_configured_cors_origin(api_db_path):
    origin = "https://products.example.com"
    application = api.create_app(
        Settings(
            database_path=str(api_db_path),
            cors_allowed_origins=(origin,),
        )
    )

    with TestClient(application) as client:
        response = client.options(
            "/products",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_api_client_starts_with_empty_database(api_client):
    response = api_client.get("/products")
    assert response.status_code == 200
    assert response.json() == {"items": [], "page": 1, "limit": 20, "total": 0}


def test_list_products(seeded_api_client):
    response = seeded_api_client.get("/products")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 20
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert body["items"][0]["name"] == "Arroz"


def test_list_products_with_pagination(seeded_api_client):
    response = seeded_api_client.get("/products?page=2&limit=2")
    assert response.status_code == 200
    assert response.json() == {
        "items": [{"id": 3, "name": "Macarrão", "price": 5.0, "version": 1}],
        "page": 2,
        "limit": 2,
        "total": 3,
    }


def test_list_products_with_name_filter_and_pagination(seeded_api_client):
    response = seeded_api_client.get("/products?name=AR&page=1&limit=1")
    assert response.status_code == 200
    assert response.json() == {
        "items": [{"id": 1, "name": "Arroz", "price": 12.0, "version": 1}],
        "page": 1,
        "limit": 1,
        "total": 2,
    }


def test_create_product(api_client):
    response = api_client.post(
        "/products",
        json={"name": "Banana", "price": 5.0},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Banana"
    assert response.json()["price"] == 5.0
    assert response.json()["version"] == 1
    assert "id" in response.json()


def test_create_product_duplicate(api_client):
    api_client.post("/products", json={"name": "Banana", "price": 5.0})
    response = api_client.post(
        "/products",
        json={"name": "Banana", "price": 10.0},
    )
    assert response.status_code == 409
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
    assert response.json()["version"] == 1


def test_get_product_not_found(seeded_api_client):
    response = seeded_api_client.get("/products/999")
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text


def test_update_product(seeded_api_client):
    product = seeded_api_client.get("/products/1").json()
    response = seeded_api_client.put(
        "/products/1",
        json={"name": "Arroz Integral", "price": 15.0, "version": product["version"]},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Arroz Integral"
    assert response.json()["price"] == 15.0
    assert response.json()["version"] == 2


def test_update_product_conflicts_with_stale_version(seeded_api_client):
    product = seeded_api_client.get("/products/1").json()
    first_update = seeded_api_client.put(
        "/products/1",
        json={"name": "Arroz Integral", "price": 15.0, "version": product["version"]},
    )
    assert first_update.status_code == 200

    response = seeded_api_client.put(
        "/products/1",
        json={
            "name": "Arroz Parboilizado",
            "price": 16.0,
            "version": product["version"],
        },
    )
    assert response.status_code == 409
    assert "alterado" in response.text


def test_update_product_not_found(seeded_api_client):
    response = seeded_api_client.put(
        "/products/999",
        json={"name": "Teste", "price": 10.0, "version": 1},
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
    assert response.status_code == 200
    assert response.json() == []
