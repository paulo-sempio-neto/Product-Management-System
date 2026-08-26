```markdown
# Sistema de Gerenciamento de Produtos

Sistema de gerenciamento de produtos com interface no terminal e API REST.

## 🚀 Funcionalidades

- CRUD completo de produtos
- API REST com FastAPI
- Banco de dados SQLite
- Testes automatizados

## 🛠️ Tecnologias

- Python, FastAPI, SQLite, Pydantic, Uvicorn, Pytest

## ⚙️ Como Executar

### Terminal
```bash
python main.py
```

### API
```bash
python -m uvicorn api:app --reload
```
Acesse: http://127.0.0.1:8000/docs

### Testes
```bash
python -m pytest tests/test_produtos.py -v
```

## 📋 Menu Principal

```
1 - Cadastrar produto
2 - Buscar produto por ID
3 - Atualizar preço
4 - Remover produto
5 - Listar todos os produtos
6 - Mostrar preço médio
7 - Listar produtos acima de um preço
8 - Buscar produtos por parte do nome
9 - Sair
```

## 📌 Decisões Técnicas

- Código em inglês, mensagens em português
- Separação de responsabilidades
- SQLite em vez de JSON
- Testes automatizados

## 📚 Documentação

- [STRUCTURE.md](./STRUCTURE.md) - Detalhes da arquitetura

## 👨‍💻 Autor

Paulo Malpice Sêmpio Neto - [paulosempioneto-collab](https://github.com/paulosempioneto-collab)
```

---