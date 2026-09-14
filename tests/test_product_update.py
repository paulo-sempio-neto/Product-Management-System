from fastapi.testclient import TestClient

import api
from database import create_table


def test_update_product_name_rules(tmp_path, monkeypatch):
    # Usa um banco temporário sem alterar seus produtos.
    db_path = str(tmp_path / "update_test.db")
    create_table(db_path)
    monkeypatch.setattr(api, "DB_NAME", db_path)

    with TestClient(api.app) as client:
        # Cadastra dois produtos para testar a duplicidade.
        first = client.post(
            "/products", json={"name": "Martelo", "price": 35.90}
        )
        second = client.post(
            "/products", json={"name": "Serrote", "price": 50.00}
        )

        assert first.status_code == 201
        assert second.status_code == 201
        product_id = second.json()["id"]

        # Impede renomear o segundo produto com o nome do primeiro.
        response = client.put(
            f"/products/{product_id}",
            json={"name": "Martelo", "price": 60.00},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Já existe outro produto com esse nome"
        )

        # Confirma que a tentativa rejeitada não alterou os dados.
        saved = client.get(f"/products/{product_id}")
        assert saved.status_code == 200
        assert saved.json()["name"] == "Serrote"
        assert saved.json()["price"] == 50.00

        # Permite alterar o preço mantendo o nome do próprio produto.
        response = client.put(
            f"/products/{product_id}",
            json={"name": "Serrote", "price": 60.00},
        )

        assert response.status_code == 200
        saved = client.get(f"/products/{product_id}")
        assert saved.json()["name"] == "Serrote"
        assert saved.json()["price"] == 60.00