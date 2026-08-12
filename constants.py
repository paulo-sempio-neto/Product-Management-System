# constants.py
# Configurações e mensagens fixas do sistema

FILE_NAME = "produtos.json"

MENU_TITLE = "=== Sistema de Produtos ==="

MENU_OPTIONS = {
    "1": "Cadastrar produto",
    "2": "Buscar produto por ID",
    "3": "Atualizar preço",
    "4": "Remover produto",
    "5": "Listar todos os produtos",
    "6": "Mostrar preço médio",
    "7": "Listar produtos acima de um preço",
    "8": "Buscar produtos por parte do nome",
    "9": "Sair"
}

ERROR_INVALID_ID = "O ID deve ser maior que zero."
ERROR_INVALID_ID_VALUE = "Digite um ID válido."
ERROR_EMPTY_NAME = "O nome do produto não pode ficar vazio."
ERROR_NEGATIVE_PRICE = "O preço não pode ser negativo."
ERROR_INVALID_OPTION = "Opção inválida."
ERROR_INVALID_PRICE = "Digite um preço válido."
ERROR_INVALID_NAME = "Nome inválido."
ERROR_PRODUCT_NOT_FOUND = "Produto não encontrado."
ERROR_PRODUCT_DUPLICATE = "Produto já cadastrado."

SUCCESS_PRODUCT_CREATED = "Produto cadastrado com sucesso."
SUCCESS_PRODUCT_UPDATED = "Produto atualizado com sucesso."
SUCCESS_PRODUCT_DELETED = "Produto removido com sucesso."

FILE_NAME = "produtos.json"

MSG_EXIT_MENU = "Saindo do sistema."
MSG_NO_PRODUCTS = "Nenhum produto cadastrado."
MSG_LOAD_SUCCESS = "Produtos carregados do arquivo produtos.json."
MSG_LOAD_ERROR = "Arquivo produtos.json não encontrado. Começando com lista vazia."
MSG_PRODUCT_LIST = "Lista de produtos:"
MSG_NO_PRODUCTS_ABOVE = "Nenhum produto encontrado nessa faixa de preço."
MSG_NO_PRODUCTS_FOUND = "Nenhum produto encontrado com esse nome."

PROMPT_MINIMUM_PRICE = "Preço mínimo: "
PROMPT_PRODUCT_ID = "ID do produto: "
PROMPT_PRODUCT_PRICE = "Preço do produto: "
PROMPT_PRODUCT_NAME = "Nome do produto: "
PROMPT_MENU_OPTION = "Escolha uma opção: "
PROMPT_PRODUCT_NAME = "Digite o nome do produto: "
PROMPT_PRODUCT_PRICE = "Digite o preço do produto: "
PROMPT_NEW_PRICE = "Digite o novo preço: "
PROMPT_PARTIAL_NAME = "Digite parte do nome: "
PROMPT_MINIMUM_PRICE = "Digite o preço mínimo: "