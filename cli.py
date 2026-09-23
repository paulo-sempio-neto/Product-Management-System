import constants
import product_service
from cli_input import (
    read_menu_option,
    read_price,
    read_product_id,
    read_product_name,
)


def create_product() -> None:
    """Cria um novo produto no banco de dados"""
    name = read_product_name(constants.PROMPT_PRODUCT_NAME)
    if name is None:
        return

    price = read_price(constants.PROMPT_PRODUCT_PRICE)

    try:
        product_service.create_product(name, price)
    except product_service.DuplicateProductError:
        print(constants.ERROR_PRODUCT_DUPLICATE)
        return
    except product_service.ProductValidationError:
        print(constants.ERROR_INVALID_NAME)
        return

    print(constants.SUCCESS_PRODUCT_CREATED)


def search_product() -> None:
    """Busca um produto pelo ID"""
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)
    if product_id is None:
        return

    try:
        product = product_service.get_product(product_id)
    except product_service.ProductNotFoundError:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    print(f"ID: {product['id']}")
    print(f"Nome: {product['name']}")
    print(f"Preço: R$ {product['price']:.2f}")


def update_product() -> None:
    """Atualiza o preço de um produto"""
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)
    if product_id is None:
        return

    try:
        product = product_service.get_product(product_id)
    except product_service.ProductNotFoundError:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    new_price = read_price(constants.PROMPT_NEW_PRICE)
    product_service.update_product(
        product_id,
        product["name"],
        new_price,
        product["version"],
    )

    print(constants.SUCCESS_PRODUCT_UPDATED)


def delete_product() -> None:
    """Remove um produto"""
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)
    if product_id is None:
        return

    try:
        product_service.delete_product(product_id)
    except product_service.ProductNotFoundError:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    print(constants.SUCCESS_PRODUCT_DELETED)


def list_products() -> None:
    """Lista todos os produtos"""
    products = product_service.list_products()
    if not products:
        print(constants.MSG_NO_PRODUCTS)
        return

    print(constants.MSG_PRODUCT_LIST)
    for product in products:
        print(f"ID {product['id']} - {product['name']}: R$ {product['price']:.2f}")


def show_average_product_price() -> None:
    """Mostra o preço médio dos produtos"""
    products = product_service.list_products()
    if not products:
        print(constants.MSG_NO_PRODUCTS)
        return

    average = product_service.calculate_average_price(products)
    print(f"Preço médio dos produtos: R$ {average:.2f}")


def list_products_above_price() -> None:
    """Lista produtos acima de um preço mínimo"""
    products = product_service.list_products()
    if not products:
        print(constants.MSG_NO_PRODUCTS)
        return

    minimum_price = read_price(constants.PROMPT_MINIMUM_PRICE)
    matching_products = product_service.filter_products_by_minimum_price(
        products,
        minimum_price,
    )

    print(f"Produtos com preço maior ou igual a R$ {minimum_price:.2f}:")
    for product in matching_products:
        print(f"ID {product['id']} - {product['name']}: R$ {product['price']:.2f}")

    if not matching_products:
        print(constants.MSG_NO_PRODUCTS_ABOVE)


def search_products_by_partial_name() -> None:
    """Busca produtos por parte do nome"""
    partial_name = input(constants.PROMPT_PARTIAL_NAME).strip().lower()
    if not partial_name:
        print(constants.ERROR_INVALID_NAME)
        return

    products = product_service.search_products(partial_name)
    if not products:
        print(constants.MSG_NO_PRODUCTS_FOUND)
        return

    print("Produtos encontrados:")
    for product in products:
        print(
            f"ID: {product['id']} | "
            f"Nome: {product['name']} | "
            f"Preço: R$ {product['price']:.2f}"
        )


def show_menu() -> None:
    """Exibe o menu principal"""
    try:
        product_service.initialize_products()
    except product_service.ProductPersistenceError:
        print(constants.ERROR_DATABASE)
        return

    while True:
        print()
        print(constants.MENU_TITLE)
        for key, value in constants.MENU_OPTIONS.items():
            print(f"{key} - {value}")

        option = read_menu_option()

        try:
            if option == "1":
                create_product()
            elif option == "2":
                search_product()
            elif option == "3":
                update_product()
            elif option == "4":
                delete_product()
            elif option == "5":
                list_products()
            elif option == "6":
                show_average_product_price()
            elif option == "7":
                list_products_above_price()
            elif option == "8":
                search_products_by_partial_name()
            elif option == "9":
                print(constants.EXIT_MESSAGE)
                break
            else:
                print(constants.ERROR_INVALID_OPTION)
        except product_service.ProductPersistenceError:
            print(constants.ERROR_DATABASE)
