from decimal import Decimal, InvalidOperation

import constants

MAX_PRICE_CENTS = 2**63 - 1


def read_price(message: str) -> Decimal:
    """Read a positive product price from the terminal."""
    while True:
        try:
            price = Decimal(input(message).strip())
            if not price.is_finite() or price <= 0:
                print(constants.ERROR_NEGATIVE_PRICE)
                continue
            cents = price * 100
            if cents != cents.to_integral_value() or int(cents) > MAX_PRICE_CENTS:
                print(constants.ERROR_INVALID_PRICE)
                continue
            return price
        except InvalidOperation:
            print(constants.ERROR_INVALID_PRICE)


def read_product_name(message: str) -> str | None:
    """Read and trim a non-empty product name from the terminal."""
    name = input(message).strip()
    if not name:
        print(constants.ERROR_EMPTY_NAME)
        return None
    return name


def read_product_id(message: str) -> int | None:
    """Read a positive product ID from the terminal."""
    try:
        product_id = int(input(message))
        if product_id <= 0:
            print(constants.ERROR_INVALID_ID)
            return None
        return product_id
    except ValueError:
        print(constants.ERROR_INVALID_ID_VALUE)
        return None


def read_menu_option() -> str:
    """Read a menu option from the terminal."""
    return input(constants.PROMPT_MENU_OPTION).strip()
