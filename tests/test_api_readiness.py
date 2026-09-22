import pytest
from fastapi.testclient import TestClient

import api
import product_service
from config import Settings
from repositories import get_repository


def test_health_checks_storage_without_modifying_it(sqlite_api_client, api_db_path):
    before = api_db_path.read_bytes()
    response = sqlite_api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert api_db_path.read_bytes() == before


def test_liveness_does_not_check_storage(api_client, monkeypatch):
    def fail_storage(*, repository):
        raise product_service.ProductPersistenceError

    monkeypatch.setattr(api, "check_product_storage", fail_storage)
    response = api_client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unavailable_health_returns_safe_503(sqlite_api_client, tmp_path):
    target = tmp_path / "missing.db"
    unavailable = get_repository(settings=Settings(database_path=str(target)))
    sqlite_api_client.app.dependency_overrides[api.get_product_repository] = lambda: (
        unavailable
    )
    response = sqlite_api_client.get("/health")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"
    assert str(target) not in response.text
    assert not target.exists()


def test_framework_errors_preserve_detail_and_headers(api_client):
    missing = api_client.get("/not-a-route")
    assert missing.status_code == 404
    assert missing.json() == {
        "detail": "Not Found",
        "error": {"code": "not_found"},
    }
    wrong_method = api_client.patch("/products/1")
    assert wrong_method.status_code == 405
    assert "allow" in wrong_method.headers
    assert wrong_method.json()["error"]["code"] == "method_not_allowed"


def test_duplicate_error_keeps_existing_contract(api_client):
    product = {"name": "Duplicate", "price": 2}
    api_client.post("/products", json=product)
    response = api_client.post("/products", json=product)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Produto já cadastrado",
        "error": {"code": "bad_request"},
    }


@pytest.mark.parametrize("price", [True, False, "nan", "inf", "-inf", "1e999"])
def test_invalid_price_is_rejected_without_echoing_input(api_client, price):
    response = api_client.post("/products", json={"name": "Test", "price": price})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    for issue in response.json()["detail"]:
        assert set(issue) == {"loc", "msg", "type"}
    assert api_client.get("/products").json() == []


def test_validation_does_not_echo_secret_input(api_client):
    response = api_client.post(
        "/products", json={"name": "Test", "price": "secret-token-example"}
    )
    assert response.status_code == 422
    assert "secret-token-example" not in response.text


def test_whitespace_name_error_is_json_serializable(api_client):
    response = api_client.post("/products", json={"name": "   ", "price": 1})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]


def test_malformed_json_uses_standard_error(api_client):
    response = api_client.post(
        "/products", content="{", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_sql_injection_payload_is_stored_as_data(api_client):
    name = "Test'); DROP TABLE products; --"
    response = api_client.post("/products", json={"name": name, "price": 1})
    assert response.status_code == 201
    assert response.json()["name"] == name
    assert api_client.get("/products").json() == [response.json()]
    assert api_client.get("/health").status_code == 200


def test_oversized_id_does_not_cause_internal_error(api_client):
    response = api_client.get(f"/products/{2**100}")
    assert response.status_code == 404


@pytest.mark.parametrize("unexpected", [False, True])
def test_internal_failures_are_sanitized(api_app, monkeypatch, unexpected):
    def fail_read(*, repository):
        error = RuntimeError if unexpected else product_service.ProductPersistenceError
        raise error("secret database path and credentials")

    monkeypatch.setattr(api, "list_products", fail_read)
    with TestClient(api_app, raise_server_exceptions=False) as client:
        response = client.get("/products")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_server_error"
    assert "secret" not in response.text


def test_openapi_documents_errors_and_health(api_client):
    schema = api_client.get("/openapi.json").json()
    assert "/health" in schema["paths"]
    assert "/live" in schema["paths"]
    assert "ErrorResponse" in schema["components"]["schemas"]
    assert schema["paths"]["/products"]["get"]["tags"] == ["products"]
