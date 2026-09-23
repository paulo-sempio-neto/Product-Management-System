def test_update_product_name_rules(api_client):
    # Cadastra dois produtos para testar a duplicidade.
    first = api_client.post("/products", json={"name": "Martelo", "price": 35.90})
    second = api_client.post("/products", json={"name": "Serrote", "price": 50.00})

    assert first.status_code == 201
    assert second.status_code == 201
    product_id = second.json()["id"]

    # Impede renomear o segundo produto com o nome do primeiro.
    response = api_client.put(
        f"/products/{product_id}",
        json={"name": "Martelo", "price": 60.00},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Já existe outro produto com esse nome")

    # Confirma que a tentativa rejeitada não alterou os dados.
    saved = api_client.get(f"/products/{product_id}")
    assert saved.status_code == 200
    assert saved.json()["name"] == "Serrote"
    assert saved.json()["price"] == 50.00

    # Permite alterar o preço mantendo o nome do próprio produto.
    response = api_client.put(
        f"/products/{product_id}",
        json={"name": "Serrote", "price": 60.00},
    )

    assert response.status_code == 200
    saved = api_client.get(f"/products/{product_id}")
    assert saved.json()["name"] == "Serrote"
    assert saved.json()["price"] == 60.00
