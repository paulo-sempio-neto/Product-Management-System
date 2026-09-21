import cli
import constants
import product_service


def test_create_product_uses_service_and_preserves_success_message(
    monkeypatch,
    capsys,
):
    recorded = {}
    monkeypatch.setattr(cli, "read_product_name", lambda _message: "Produto")
    monkeypatch.setattr(cli, "read_price", lambda _message: 10.0)

    def create_product(name, price):
        recorded["name"] = name
        recorded["price"] = price

    monkeypatch.setattr(product_service, "create_product", create_product)

    cli.create_product()

    assert recorded == {"name": "Produto", "price": 10.0}
    assert capsys.readouterr().out.strip() == constants.SUCCESS_PRODUCT_CREATED


def test_create_product_preserves_duplicate_message(monkeypatch, capsys):
    monkeypatch.setattr(cli, "read_product_name", lambda _message: "Produto")
    monkeypatch.setattr(cli, "read_price", lambda _message: 10.0)

    def reject_duplicate(_name, _price):
        raise product_service.DuplicateProductError

    monkeypatch.setattr(product_service, "create_product", reject_duplicate)

    cli.create_product()

    assert capsys.readouterr().out.strip() == constants.ERROR_PRODUCT_DUPLICATE


def test_update_missing_product_does_not_prompt_for_price(monkeypatch, capsys):
    monkeypatch.setattr(cli, "read_product_id", lambda _message: 999)

    def missing_product(_product_id):
        raise product_service.ProductNotFoundError

    def unexpected_price_prompt(_message):
        raise AssertionError("Price should not be requested for a missing product")

    monkeypatch.setattr(product_service, "get_product", missing_product)
    monkeypatch.setattr(cli, "read_price", unexpected_price_prompt)

    cli.update_product()

    assert capsys.readouterr().out.strip() == constants.ERROR_PRODUCT_NOT_FOUND


def test_list_products_preserves_cli_output(monkeypatch, capsys):
    monkeypatch.setattr(
        product_service,
        "list_products",
        lambda: [{"id": 1, "name": "Produto", "price": 12.5}],
    )

    cli.list_products()

    assert capsys.readouterr().out.splitlines() == [
        constants.MSG_PRODUCT_LIST,
        "ID 1 - Produto: R$ 12.50",
    ]
