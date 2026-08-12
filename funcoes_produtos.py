import json


def read_price(message: str) -> float:
    while True:
        try:
            price = float(input(message))

            if price < 0:
                print("O preço não pode ser negativo.")
                continue

            return price

        except ValueError:
            print("Digite um preço válido.")


def read_product_name(message: str) -> None | str:
    name = input(message).strip().title()

    if name == "":
        print("O nome do produto não pode ficar vazio.")
        return None

    return name


def read_product_id(message: str) -> int | None:
    try:
        product_id = int(input(message))

        if product_id <= 0:
            print("O ID deve ser maior que zero.")
            return None

        return product_id

    except ValueError:
        print("Digite um ID válido.")
        return None


def read_menu_option() -> str:
    return input("Escolha uma opção: ").strip()


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
    name = read_product_name("Nome do produto: ")

    if name is None:
        return

    existing_product = find_product_by_name(products, name)

    if existing_product is not None:
        print("Produto já cadastrado.")
        return

    price = read_price("Preço do produto: ")
    product_id = generate_next_id(products)

    product = {
        "id": product_id,
        "name": name,
        "price": price
    }

    products.append(product)
    save_products(products)

    print("Produto cadastrado com sucesso.")


def search_product(products: list) -> None:
    product_id = read_product_id("ID do produto: ")

    if product_id is None:
        return

    product = find_product_by_id(products, product_id)

    if product is None:
        print("Produto não encontrado.")
        return

    print(f"ID: {product['id']}")
    print(f"Produto: {product['name']}")
    print(f"Preço: R$ {product['price']:.2f}")


def update_product(products: list) -> None:
    product_id = read_product_id("ID do produto: ")

    if product_id is None:
        return

    product = find_product_by_id(products, product_id)

    if product is None:
        print("Produto não encontrado.")
        return

    new_price = read_price("Novo preço do produto: ")

    product["price"] = new_price
    save_products(products)

    print("Produto atualizado com sucesso.")


def delete_product(products: list) -> None:
    product_id = read_product_id("ID do produto: ")

    if product_id is None:
        return

    product = find_product_by_id(products, product_id)

    if product is None:
        print("Produto não encontrado.")
        return

    products.remove(product)
    save_products(products)

    print("Produto removido com sucesso.")


def list_products(products: list) -> None:
    if len(products) == 0:
        print("Nenhum produto cadastrado.")
        return

    print("Lista de produtos:")

    for product in products:
        print(f"ID {product['id']} - {product['name']}: R$ {product['price']:.2f}")


def save_products(products: list) -> None:
    with open("produtos.json", "w", encoding="utf-8") as products_file:
        json.dump(products, products_file, ensure_ascii=False, indent=4)


def load_products() -> list:
    try:
        with open("produtos.json", "r", encoding="utf-8") as products_file:
            print("Produtos carregados do arquivo produtos.json.")
            return json.load(products_file)

    except FileNotFoundError:
        print("Arquivo produtos.json não encontrado. Começando com lista vazia.")
        return []


def show_average_product_price(products: list) -> None:
    if len(products) == 0:
        print("Nenhum produto cadastrado.")
        return

    total_value = 0

    for product in products:
        total_value += product["price"]

    average_price = total_value / len(products)

    print(f"Preço médio dos produtos: R$ {average_price:.2f}")


def list_products_above_price(products: list) -> None:
    if len(products) == 0:
        print("Nenhum produto cadastrado.")
        return

    minimum_price = read_price("Preço mínimo: ")

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
        print("Nenhum produto encontrado nessa faixa de preço.")


def filter_products_by_partial_name(products: list, partial_name: str) -> list:
    found_products = []

    for product in products:
        if partial_name in product["name"].lower():
            found_products.append(product)

    return found_products


def search_products_by_partial_name(products: list) -> None:
    if len(products) == 0:
        print("Nenhum produto cadastrado.")
        return

    partial_name = input("Digite parte do nome do produto: ").strip().lower()

    if partial_name == "":
        print("Nome inválido.")
        return

    found_products = filter_products_by_partial_name(products, partial_name)

    if len(found_products) == 0:
        print("Nenhum produto encontrado com esse nome.")
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
        print("=== Sistema de Produtos ===")
        print("1 - Cadastrar produto")
        print("2 - Buscar produto")
        print("3 - Atualizar produto")
        print("4 - Remover produto")
        print("5 - Listar produtos")
        print("6 - Mostrar preço médio dos produtos")
        print("7 - Listar produtos acima de um preço")
        print("8 - Buscar produtos por parte do nome")
        print("9 - Sair")

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
            print("Saindo do sistema.")
            break

        else:
            print("Opção inválida.")