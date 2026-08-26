import constants
from database import (
    load_products,
    save_products,
    generate_next_id,
    find_product_by_id,
    find_product_by_name,
    filter_products_by_partial_name,
    create_table
)
from funcoes_produtos import (
    read_product_name,
    read_product_id,
    read_price,
    read_menu_option
)


def create_product():
    """Cria um novo produto no banco de dados"""
    name = read_product_name(constants.PROMPT_PRODUCT_NAME)
    if name is None:
        return

    existing = find_product_by_name(name)
    if existing:
        print(constants.ERROR_PRODUCT_DUPLICATE)
        return

    price = read_price(constants.PROMPT_PRODUCT_PRICE)
    new_id = generate_next_id()

    new_product = {
        "id": new_id,
        "name": name,
        "price": price
    }

    products = load_products()
    products.append(new_product)
    save_products(products)

    print(constants.SUCCESS_PRODUCT_CREATED)


def search_product():
    """Busca um produto pelo ID"""
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)
    if product_id is None:
        return

    product = find_product_by_id(product_id)
    if product is None:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    print(f"ID: {product['id']}")
    print(f"Nome: {product['name']}")
    print(f"Preço: R$ {product['price']:.2f}")


def update_product():
    """Atualiza o preço de um produto"""
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)
    if product_id is None:
        return

    product = find_product_by_id(product_id)
    if product is None:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    new_price = read_price(constants.PROMPT_NEW_PRICE)
    
    products = load_products()
    for p in products:
        if p["id"] == product_id:
            p["price"] = new_price
            break
    save_products(products)

    print(constants.SUCCESS_PRODUCT_UPDATED)


def delete_product():
    """Remove um produto"""
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)
    if product_id is None:
        return

    product = find_product_by_id(product_id)
    if product is None:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    products = load_products()
    products = [p for p in products if p["id"] != product_id]
    save_products(products)

    print(constants.SUCCESS_PRODUCT_DELETED)


def list_products():
    """Lista todos os produtos"""
    products = load_products()
    if not products:
        print(constants.MSG_NO_PRODUCTS)
        return

    print(constants.MSG_PRODUCT_LIST)
    for product in products:
        print(f"ID {product['id']} - {product['name']}: R$ {product['price']:.2f}")


def show_average_product_price():
    """Mostra o preço médio dos produtos"""
    products = load_products()
    if not products:
        print(constants.ERROR_NO_PRODUCTS)
        return

    total = sum(p["price"] for p in products)
    average = total / len(products)
    print(f"Preço médio dos produtos: R$ {average:.2f}")


def list_products_above_price():
    """Lista produtos acima de um preço mínimo"""
    products = load_products()
    if not products:
        print(constants.ERROR_NO_PRODUCTS)
        return

    minimum_price = read_price(constants.PROMPT_MINIMUM_PRICE)
    
    found = False
    print(f"Produtos com preço maior ou igual a R$ {minimum_price:.2f}:")
    
    for product in products:
        if product["price"] >= minimum_price:
            print(f"ID {product['id']} - {product['name']}: R$ {product['price']:.2f}")
            found = True
    
    if not found:
        print(constants.MSG_NO_PRODUCTS_ABOVE)


def search_products_by_partial_name():
    """Busca produtos por parte do nome"""
    partial_name = input(constants.PROMPT_PARTIAL_NAME).strip().lower()
    if not partial_name:
        print(constants.ERROR_INVALID_NAME)
        return

    products = filter_products_by_partial_name(partial_name)
    if not products:
        print(constants.MSG_NO_PRODUCTS_FOUND)
        return

    print("Produtos encontrados:")
    for product in products:
        print(f"ID: {product['id']} | Nome: {product['name']} | Preço: R$ {product['price']:.2f}")


def show_menu():
    """Exibe o menu principal"""
    create_table()  # Garante que a tabela existe

    while True:
        print()
        print(constants.MENU_TITLE)
        for key, value in constants.MENU_OPTIONS.items():
            print(f"{key} - {value}")

        option = read_menu_option()

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


if __name__ == "__main__":
    show_menu()