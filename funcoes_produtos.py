import json
import constants


def read_price(message: str) -> float:
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
    name = input(message).strip().title()

    if name == "":
        print(constants.ERROR_EMPTY_NAME)
        return None

    return name


def read_product_id(message: str) -> int | None:
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
    return input(constants.PROMPT_MENU_OPTION).strip()


def find_product_by_name(products: list, name: str) -> dict | None:
    for product in products:
        if product["name"] == name:
            return product

    return None


def find_product_by_id(products: list, product_id: int) -> dict | None:
    for product in products:
        if product["id"] == product_id:
            return product

    return None


def generate_next_id(products: list) -> int:
    if len(products) == 0:
        return 1

    last_product = products[-1]

    return last_product["id"] + 1


def create_product(products: list) -> None:
    name = read_product_name(constants.PROMPT_PRODUCT_NAME)

    if name is None:
        return

    existing_product = find_product_by_name(products, name)

    if existing_product is not None:
        print(constants.ERROR_PRODUCT_DUPLICATE)
        return

    price = read_price(constants.PROMPT_PRODUCT_PRICE )
    product_id = generate_next_id(products)

    product = {
        "id": product_id,
        "name": name,
        "price": price
    }

    products.append(product)
    save_products(products)

    print(constants.SUCCESS_PRODUCT_CREATED)


def search_product(products: list) -> None:
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)

    if product_id is None:
        return

    product = find_product_by_id(products, product_id)

    if product is None:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    print(f"ID: {product['id']}")
    print(f"Produto: {product['name']}")
    print(f"Preço: R$ {product['price']:.2f}")


def update_product(products: list) -> None:
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)

    if product_id is None:
        return

    product = find_product_by_id(products, product_id)

    if product is None:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    new_price = read_price(constants.PROMPT_NEW_PRICE)

    product["price"] = new_price
    save_products(products)

    print(constants.SUCCESS_PRODUCT_UPDATED)


def delete_product(products: list) -> None:
    product_id = read_product_id(constants.PROMPT_PRODUCT_ID)

    if product_id is None:
        return

    product = find_product_by_id(products, product_id)

    if product is None:
        print(constants.ERROR_PRODUCT_NOT_FOUND)
        return

    products.remove(product)
    save_products(products)

    print(constants.SUCCESS_PRODUCT_DELETED)


def list_products(products: list) -> None:
    if len(products) == 0:
        print(constants.ERROR_NO_PRODUCTS)
        return

    print(constants.MSG_PRODUCT_LIST)

    for product in products:
        print(f"ID {product['id']} - {product['name']}: R$ {product['price']:.2f}")


def save_products(products: list) -> None:
    with open(constants.FILE_NAME, "w", encoding="utf-8") as products_file:
        json.dump(products, products_file, ensure_ascii=False, indent=4)


def load_products() -> list:
    try:
        with open(constants.FILE_NAME, "r", encoding="utf-8") as products_file:
            print(constants.MSG_LOAD_SUCCESS)
            return json.load(products_file)

    except FileNotFoundError:
        print(constants.MSG_LOAD_ERROR)
        return []


def show_average_product_price(products: list) -> None:
    if len(products) == 0:
        print(constants.MSG_NO_PRODUCTS)
        return

    total_value = 0

    for product in products:
        total_value += product["price"]

    average_price = total_value / len(products)

    print(f"Preço médio dos produtos: R$ {average_price:.2f}")


def list_products_above_price(products: list) -> None:
    if len(products) == 0:
        print(constants.MSG_NO_PRODUCTS)
        return

    minimum_price = read_price(constants.PROMPT_MINIMUM_PRICE)

    found_product = False

    print(f"Produtos com preço maior ou igual a R$ {minimum_price:.2f}:")

    for product in products:
        if product["price"] >= minimum_price:
            product_id = product["id"]
            name = product["name"]
            price = product["price"]

            print(f"ID {product_id} - {name}: R$ {price:.2f}")

            found_product = True

    if found_product == False:
        print(constants.MSG_NO_PRODUCTS_ABOVE)


def filter_products_by_partial_name(products: list, partial_name: str) -> list:
    found_products = []

    for product in products:
        if partial_name in product["name"].lower():
            found_products.append(product)

    return found_products


def search_products_by_partial_name(products: list) -> None:
    if len(products) == 0:
        print(constants.MSG_NO_PRODUCTS)
        return

    partial_name = input(constants.PROMPT_PARTIAL_NAME).strip().lower()

    if partial_name == "":
        print(constants.ERROR_INVALID_NAME)
        return

    found_products = filter_products_by_partial_name(products, partial_name)

    if len(found_products) == 0:
        print(constants.MSG_NO_PRODUCTS_FOUND)
        return

    print(f"Produtos encontrados com \"{partial_name}\":")

    for product in found_products:
        product_id = product["id"]
        name = product["name"]
        price = product["price"]

        print(f"ID {product_id} - {name}: R$ {price:.2f}")


def show_menu(products: list) -> None:
    while True:
        print()
        print(constants.MENU_TITLE)
        for key, value in constants.MENU_OPTIONS.items():
            print(f"{key} - {value}")

        option = read_menu_option()

        if option == "1":
            create_product(products)

        elif option == "2":
            search_product(products)

        elif option == "3":
            update_product(products)

        elif option == "4":
            delete_product(products)

        elif option == "5":
            list_products(products)

        elif option == "6":
            show_average_product_price(products)

        elif option == "7":
            list_products_above_price(products)

        elif option == "8":
            search_products_by_partial_name(products)

        elif option == "9":
            print(constants.MSG_EXIT_MENU)
            break

        else:
            print(constants.ERROR_INVALID_OPTION)