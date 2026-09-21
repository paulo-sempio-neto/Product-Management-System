import builtins

import cli_input
import constants


def test_read_price_retries_after_invalid_and_non_positive_values(
    monkeypatch,
    capsys,
):
    responses = iter(["invalid", "0", "12.5"])
    monkeypatch.setattr(builtins, "input", lambda _message: next(responses))

    assert cli_input.read_price("Price: ") == 12.5
    assert capsys.readouterr().out.splitlines() == [
        constants.ERROR_INVALID_PRICE,
        constants.ERROR_NEGATIVE_PRICE,
    ]


def test_read_product_name_trims_valid_input(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda _message: "  Product  ")

    assert cli_input.read_product_name("Name: ") == "Product"
    assert capsys.readouterr().out == ""


def test_read_product_name_reports_empty_input(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda _message: "   ")

    assert cli_input.read_product_name("Name: ") is None
    assert capsys.readouterr().out.strip() == constants.ERROR_EMPTY_NAME


def test_read_product_id_reports_invalid_numeric_input(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda _message: "0")

    assert cli_input.read_product_id("ID: ") is None
    assert capsys.readouterr().out.strip() == constants.ERROR_INVALID_ID


def test_read_product_id_reports_non_numeric_input(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda _message: "invalid")

    assert cli_input.read_product_id("ID: ") is None
    assert capsys.readouterr().out.strip() == constants.ERROR_INVALID_ID_VALUE


def test_read_menu_option_strips_terminal_input(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _message: "  1  ")

    assert cli_input.read_menu_option() == "1"
