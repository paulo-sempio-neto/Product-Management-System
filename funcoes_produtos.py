import json

def ler_preco(mensagem):
    """
    Lê um preço digitado pelo usuário.

    Continua pedindo enquanto o valor não for um número válido
    ou enquanto o preço for negativo.
    """
    while True:
        try:
            preco = float(input(mensagem))

            if preco < 0:
                print("O preço não pode ser negativo.")
                continue

            return preco

        except ValueError:
            print("Digite um preço válido.")


def ler_nome_produto(mensagem):
    """
    Lê o nome de um produto.

    Remove espaços extras com strip() e deixa o nome formatado com title().
    Se o nome estiver vazio, retorna None.
    """
    nome = input(mensagem).strip().title()

    if nome == "":
        print("O nome do produto não pode ficar vazio.")
        return None

    return nome


def ler_id_produto(mensagem):
    """
    Lê o ID de um produto.

    O ID precisa ser um número inteiro maior que zero.
    Se for inválido, retorna None.
    """
    try:
        id_produto = int(input(mensagem))

        if id_produto <= 0:
            print("O ID deve ser maior que zero.")
            return None

        return id_produto

    except ValueError:
        print("Digite um ID válido.")
        return None


def ler_opcao_menu():
    """
    Lê a opção escolhida pelo usuário no menu.
    """
    return input("Escolha uma opção: ").strip()


def encontrar_produto_por_nome(produtos, nome):
    """
    Procura um produto pelo nome.

    Parâmetros:
    produtos: lista de produtos cadastrados.
    nome: nome do produto que será procurado.

    Retorna:
    O produto encontrado ou None se não encontrar.
    """
    for produto in produtos:
        if produto["nome"] == nome:
            return produto

    return None


def encontrar_produto_por_id(produtos, id_produto):
    """
    Procura um produto pelo ID.

    Parâmetros:
    produtos: lista de produtos cadastrados.
    id_produto: ID do produto que será procurado.

    Retorna:
    O produto encontrado ou None se não encontrar.
    """
    for produto in produtos:
        if produto["id"] == id_produto:
            return produto

    return None


def gerar_proximo_id(produtos):
    """
    Gera o próximo ID para um novo produto.

    Se ainda não existir nenhum produto, o primeiro ID será 1.
    Caso contrário, pega o ID do último produto e soma 1.
    """
    if len(produtos) == 0:
        return 1

    ultimo_produto = produtos[-1]
    return ultimo_produto["id"] + 1


def cadastrar_produto(produtos):
    """
    Cadastra um novo produto na lista.

    O cadastro só acontece se:
    - o nome não estiver vazio;
    - o produto ainda não estiver cadastrado;
    - o preço for válido.
    """
    nome = ler_nome_produto("Nome do produto: ")

    if nome is None:
        return

    # Verifica se já existe um produto com esse nome
    produto_encontrado = encontrar_produto_por_nome(produtos, nome)

    if produto_encontrado is not None:
        print("Produto já cadastrado.")
        return

    preco = ler_preco("Preço do produto: ")

    id_produto = gerar_proximo_id(produtos)

    # Cria um dicionário representando o produto
    produto = {
        "id": id_produto,
        "nome": nome,
        "preco": preco
    }

    # Adiciona o produto dentro da lista de produtos
    produtos.append(produto)
    salvar_produtos(produtos)
    print("Produto cadastrado com sucesso.")


def buscar_produto(produtos):
    """
    Busca um produto pelo ID e mostra suas informações.
    """
    id_produto = ler_id_produto("ID do produto: ")

    if id_produto is None:
        return

    produto = encontrar_produto_por_id(produtos, id_produto)

    if produto is None:
        print("Produto não encontrado.")
        return

    print(f"ID: {produto['id']}")
    print(f"Produto: {produto['nome']}")
    print(f"Preço: R$ {produto['preco']:.2f}")


def atualizar_produto(produtos):
    """
    Atualiza o preço de um produto pelo ID.
    """
    id_produto = ler_id_produto("ID do produto: ")

    if id_produto is None:
        return

    produto = encontrar_produto_por_id(produtos, id_produto)

    if produto is None:
        print("Produto não encontrado.")
        return

    novo_preco = ler_preco("Novo preço do produto: ")

    # Altera apenas o preço do produto encontrado
    produto["preco"] = novo_preco
    salvar_produtos(produtos)
    print("Produto atualizado com sucesso.")


def remover_produto(produtos):
    """
    Remove um produto da lista pelo ID.
    """
    id_produto = ler_id_produto("ID do produto: ")

    if id_produto is None:
        return

    produto = encontrar_produto_por_id(produtos, id_produto)

    if produto is None:
        print("Produto não encontrado.")
        return

    produtos.remove(produto)
    salvar_produtos(produtos)
    print("Produto removido com sucesso.")


def listar_produtos(produtos):
    """
    Lista todos os produtos cadastrados.
    """
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return

    print("Lista de produtos:")

    # Percorre cada produto dentro da lista de produtos
    for produto in produtos:
        print(f"ID {produto['id']} - {produto['nome']}: R$ {produto['preco']:.2f}")


def salvar_produtos(produtos):
    """
    Salva a lista de produtos em um arquivo JSON.
    """
    with open("produtos.json", "w", encoding="utf-8") as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def carregar_produtos():
    """
    Carrega os produtos salvos no arquivo JSON.

    Se o arquivo ainda não existir, retorna uma lista vazia.
    """
    try:
        with open("produtos.json", "r", encoding="utf-8") as arquivo:
            print("Produtos carregados do arquivo produtos.json.")
            return json.load(arquivo)

    except FileNotFoundError:
        print("Arquivo produtos.json não encontrado. Começando com lista vazia.")
        return []


def mostrar_preco_medio_produtos(produtos):
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return

    valor_total = 0

    for produto in produtos:
        valor_total += produto["preco"]

    preco_medio = valor_total / len(produtos)

    print(f"Preço médio dos produtos: R$ {preco_medio:.2f}")


def listar_produtos_acima_do_preco(produtos):
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return

    preco_minimo = ler_preco("Preço mínimo: ")

    encontrou_produto = False

    print(f"Produtos com preço maior ou igual a R$ {preco_minimo:.2f}:")

    for produto in produtos:
        if produto["preco"] >= preco_minimo:
            produto_id = produto["id"]
            nome = produto["nome"]
            preco = produto["preco"]

            print(f"ID {produto_id} - {nome}: R$ {preco:.2f}")

            encontrou_produto = True

    if encontrou_produto == False:
        print("Nenhum produto encontrado nessa faixa de preço.")
        

def filtrar_produtos_por_parte_do_nome(produtos, parte_nome):
    produtos_encontrados = []

    for produto in produtos:
        if parte_nome in produto["nome"].lower():
            produtos_encontrados.append(produto)

    return produtos_encontrados


def buscar_produtos_por_parte_do_nome(produtos):
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return

    parte_nome = input("Digite parte do nome do produto: ").strip().lower()

    if parte_nome == "":
        print("Nome inválido.")
        return

    produtos_encontrados = filtrar_produtos_por_parte_do_nome(produtos, parte_nome)

    if len(produtos_encontrados) == 0:
        print("Nenhum produto encontrado com esse nome.")
        return

    print(f"Produtos encontrados com \"{parte_nome}\":")

    for produto in produtos_encontrados:
        produto_id = produto["id"]
        nome = produto["nome"]
        preco = produto["preco"]

        print(f"ID {produto_id} - {nome}: R$ {preco:.2f}")


def mostrar_menu(produtos):
    """
    Mostra o menu principal do sistema.

    Essa função controla o programa inteiro,
    chamando a função correta de acordo com a opção escolhida.
    """
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
    
        opcao = ler_opcao_menu()

        if opcao == "1":
            cadastrar_produto(produtos)

        elif opcao == "2":
            buscar_produto(produtos)

        elif opcao == "3":
            atualizar_produto(produtos)

        elif opcao == "4":
            remover_produto(produtos)

        elif opcao == "5":
            listar_produtos(produtos)
        
        elif opcao == "6":
            mostrar_preco_medio_produtos(produtos)

        elif opcao == "7":
            listar_produtos_acima_do_preco(produtos)

        elif opcao == "8":
            buscar_produtos_por_parte_do_nome(produtos)

        elif opcao == "9":      
            print("Saindo do sistema.")
            break

        else:
            print("Opção inválida.")
