# Importa as funções que estão no arquivo funcoes_produtos.py
# mostrar_menu: mostra o menu principal do sistema
# carregar_produtos: carrega os produtos salvos no arquivo JSON
from funcoes_produtos import mostrar_menu, carregar_produtos


# Carrega a lista de produtos que já estavam salvos no arquivo produtos.json
# Se o arquivo não existir, a função retorna uma lista vazia
produtos = carregar_produtos()


# Chama o menu principal do programa
# A lista de produtos é enviada para o menu, para que ele possa cadastrar,
# listar, alterar ou remover produtos
mostrar_menu(produtos)