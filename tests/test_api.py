
from fastapi.testclient import TestClient
import api
from api import app
from database import create_table, create_product, clear_products

# ============================================
# CONFIGURAÇÃO
# ============================================

TEST_DB = "test_api.db"

client = TestClient(app)


def setup():

    clear_products(TEST_DB)

    create_table(TEST_DB)

    create_product("Arroz", 12.0, TEST_DB)
    create_product("Feijão", 8.0, TEST_DB)
    create_product("Macarrão", 5.0, TEST_DB)

    api.DB_NAME = TEST_DB


def teardown():
    """Limpa o banco depois de cada teste"""
    clear_products()


# ============================================
# TESTES DA API
# ============================================

def test_root():
    """Testa a rota raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API de Produtos!"}


def test_list_products():
    """Testa GET /products"""
    setup()
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["name"] == "Arroz"
    teardown()


def test_create_product():
    """Testa POST /products"""
    setup()
    response = client.post(
        "/products",
        json={"name": "Banana", "price": 5.0}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Banana"
    assert response.json()["price"] == 5.0
    assert "id" in response.json()
    teardown()


def test_create_product_duplicate():
    """Testa POST /products com nome duplicado"""
    setup()
    client.post("/products", json={"name": "Banana", "price": 5.0})
    response = client.post("/products", json={"name": "Banana", "price": 10.0})
    assert response.status_code == 400
    assert "Produto já cadastrado" in response.text
    teardown()


def test_create_product_invalid_price():
    """Testa POST /products com preço negativo"""
    setup()
    response = client.post(
        "/products",
        json={"name": "Teste", "price": -10.0}
    )
    assert response.status_code == 422
    teardown()


def test_create_product_empty_name():
    """Testa POST /products com nome vazio"""
    setup()
    response = client.post(
        "/products",
        json={"name": "", "price": 10.0}
    )
    assert response.status_code == 422
    teardown()


def test_get_product_by_id():
    """Testa GET /products/{product_id}"""
    setup()
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Arroz"
    assert response.json()["price"] == 12.0
    teardown()


def test_get_product_not_found():
    """Testa GET /products/{product_id} com ID inexistente"""
    setup()
    response = client.get("/products/999")
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text
    teardown()


def test_update_product():
    """Testa PUT /products/{product_id}"""
    setup()
    response = client.put(
        "/products/1",
        json={"name": "Arroz Integral", "price": 15.0}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Arroz Integral"
    assert response.json()["price"] == 15.0
    teardown()


def test_update_product_not_found():
    """Testa PUT /products/{product_id} com ID inexistente"""
    setup()
    response = client.put(
        "/products/999",
        json={"name": "Teste", "price": 10.0}
    )
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text
    teardown()


def test_delete_product():
    """Testa DELETE /products/{product_id}"""
    setup()
    response = client.delete("/products/1")
    assert response.status_code == 204
    response = client.get("/products/1")
    assert response.status_code == 404
    teardown()


def test_delete_product_not_found():
    """Testa DELETE /products/{product_id} com ID inexistente"""
    setup()
    response = client.delete("/products/999")
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text
    teardown()


def test_search_products():
    """Testa GET /products/search/?name=..."""
    setup()
    response = client.get("/products/search/?name=ar")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Arroz"
    assert response.json()[1]["name"] == "Macarrão"
    teardown()


def test_search_products_not_found():
    """Testa GET /products/search/?name=... sem resultados"""
    setup()
    response = client.get("/products/search/?name=xyz")
    assert response.status_code == 404
    assert "Nenhum produto encontrado" in response.text
    teardown()