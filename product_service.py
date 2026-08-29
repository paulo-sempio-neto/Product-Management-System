import constants

# ============================================
# FUNÇÕES DE INTERAÇÃO COM O USUÁRIO
# ============================================

def read_price(message: str) -> float:
    """Lê e valida o preço do produto (deve ser maior que zero)"""
    while True:
        try:
            price = float(input(message))
            if price < 0:
                print(constants.ERROR_NEGATIVE_PRICE)
                continue
            return price
        except ValueError:
            print(constants.ERROR_INVALID_PRICE)


def read_product_name(message: str) -> None | str:
    """Lê e valida o nome do produto (não pode ser vazio)"""
    name = input(message).strip().title()
    if not name:
        print(constants.ERROR_EMPTY_NAME)
        return None
    return name


def read_product_id(message: str) -> int | None:
    """Lê e valida o ID do produto (deve ser maior que zero)"""
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
    """Lê a opção do menu"""
    return input(constants.PROMPT_MENU_OPTION).strip()