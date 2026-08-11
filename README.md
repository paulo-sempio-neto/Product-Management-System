# Sistema de Gerenciamento de Produtos

Sistema de linha de comando para gerenciamento de produtos com persistência em JSON.

## Funcionalidades

- Cadastrar produtos
- Buscar produto por ID
- Atualizar preço
- Remover produto
- Listar todos os produtos
- Calcular preço médio
- Filtrar por preço mínimo
- Buscar por parte do nome
- Persistência automática em JSON

## Tecnologias

- Python 3
- JSON para persistência
- Git para versionamento

## Estrutura do Projeto

```
Sistema_Produtos/
├── main.py                 # Interface com o usuário
├── funcoes_produtos.py     # Regras de negócio
├── produtos.json           # Banco de dados (JSON)
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Documentação
```

## Como Executar

```bash
python main.py
```

## Menu Principal

```
=== SISTEMA DE PRODUTOS ===
1. Cadastrar produto
2. Buscar produto por ID
3. Atualizar preço
4. Remover produto
5. Listar todos os produtos
6. Mostrar preço médio
7. Listar produtos acima ou igual a um preço
8. Buscar produtos por parte do nome
9. Sair
```

## Estrutura do Produto

```json
{
    "id": 1,
    "name": "Arroz",
    "price": 12.0
}
```

## Decisões Técnicas

- Código interno em inglês (identificadores, funções, variáveis)
- Mensagens ao usuário em português
- Separação entre lógica e interação
- Persistência automática a cada alteração
- Validações robustas (nome, preço, ID)

## Autor

Paulo Malpice Sêmpio Neto - [paulosempioneto-collab](https://github.com/paulosempioneto-collab)
```
