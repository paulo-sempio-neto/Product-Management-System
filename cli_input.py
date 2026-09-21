import math

import constants


def read_price(message: str) -> float:
    """Read a positive product price from the terminal."""
    while True:
        try:
            price = float(input(message))
            if not math.isfinite(price) or price <= 0:
                print(constants.ERROR_NEGATIVE_PRICE)
                continue
            return price
        except ValueError:
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
