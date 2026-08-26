```markdown
# Estrutura do Projeto - Sistema_Produtos

## Visão Geral
Sistema de gerenciamento de produtos com:
- Interface no terminal
- API REST com FastAPI
- Banco de dados SQLite
- Testes automatizados com pytest

---

## Arquivos e Responsabilidades

| Arquivo | Responsabilidade |
|---------|------------------|
| `main.py` | Ponto de entrada do terminal. Executa o menu. |
| `menu.py` | Menu interativo para o usuário. Chama as funções do `database.py`. |
| `api.py` | API REST com FastAPI. Fornece endpoints para gerenciar produtos. |
| `database.py` | Conexão e operações com SQLite (CRUD). |
| `constants.py` | Constantes e mensagens do sistema (mensagens, prompts, etc.). |
| `tests/test_produtos.py` | Testes automatizados com pytest. |
| `produtos.db` | Banco de dados SQLite (gerado automaticamente). |
| `.gitignore` | Arquivos ignorados pelo Git. |
| `README.md` | Documentação do projeto. |
| `STRUCTURE.md` | Estrutura do projeto (este arquivo). |

---

## Fluxo de Dados

### Terminal (main.py)
```
main.py
    ↓
menu.py
    ↓
database.py
    ↓
produtos.db
```

### API (FastAPI)
```
api.py
    ↓
database.py
    ↓
produtos.db
```

### Testes
```
tests/test_produtos.py
    ↓
database.py
    ↓
produtos.db (teste)
```

---

## Conexões entre Arquivos

- `menu.py` importa de:
  - `database.py` (operações de banco)
  - `funcoes_produtos.py` (interação com usuário)
  - `constants.py` (constantes)

- `api.py` importa de:
  - `database.py` (operações de banco)
  - `pydantic` (validação de dados)
  - `fastapi` (framework)

- `tests/test_produtos.py` importa de:
  - `database.py` (operações de banco)

---

## Como Executar

### Terminal
```bash
python main.py
```

### API
```bash
python -m uvicorn api:app --reload
```

### Testes
```bash
python -m pytest tests/test_produtos.py -v
```

---

## Tecnologias Utilizadas

- **Python 3.14**
- **FastAPI** - API REST
- **SQLite3** - Banco de dados
- **Pydantic** - Validação de dados
- **Pytest** - Testes automatizados
- **Uvicorn** - Servidor ASGI
- **Git** - Versionamento

---

## Decisões Técnicas

- **Código interno em inglês** (identificadores, funções, variáveis)
- **Mensagens ao usuário em português**
- **Separação de responsabilidades** (interação, banco, API)
- **Persistência em SQLite** (substituindo o JSON)
- **Testes automatizados** para garantir funcionamento
```

---