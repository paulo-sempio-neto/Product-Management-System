# Project Structure - Product Management System

## Overview

This project is a product management system built with Python.

It includes:

- Terminal user interface
- REST API using FastAPI
- SQLite database integration
- Automated tests with Pytest

The project is organized into independent modules to separate responsibilities and improve maintainability.

---

# Files and Responsibilities

| File | Responsibility |
|------|----------------|
| `main.py` | Application entry point. Starts the terminal interface. |
| `menu.py` | Handles the interactive terminal menu and user navigation. |
| `funcoes_produtos.py` | Contains product-related functions and user interaction logic. |
| `api.py` | FastAPI REST API implementation and endpoint management. |
| `database.py` | Handles SQLite connection and database CRUD operations. |
| `constants.py` | Stores system constants, messages, and prompts. |
| `tests/test_produtos.py` | Automated tests using Pytest. |
| `produtos.db` | SQLite database file generated during execution. |
| `.gitignore` | Defines files ignored by Git. |
| `README.md` | Main project documentation. |
| `STRUCTURE.md` | Detailed project architecture documentation. |

---

# Data Flow

## Terminal Application

```
main.py

    ↓

menu.py

    ↓

funcoes_produtos.py

    ↓

database.py

    ↓

produtos.db
```

---

## REST API

```
api.py

    ↓

database.py

    ↓

produtos.db
```

---

## Automated Tests

```
tests/test_produtos.py

    ↓

database.py

    ↓

test database
```

---

# File Dependencies

## `main.py`

Imports:

- `menu.py`

Responsibility:

- Starts the application flow.

---

## `menu.py`

Imports:

- `database.py`
- `funcoes_produtos.py`
- `constants.py`

Responsibility:

- Controls user interaction through the terminal.

---

## `api.py`

Imports:

- `database.py`
- `fastapi`
- `pydantic`

Responsibility:

- Provides REST API endpoints.
- Validates API data.
- Handles HTTP requests.

---

## `tests/test_produtos.py`

Imports:

- `database.py`

Responsibility:

- Validates database operations and product functionality.

---

# How to Run

## Terminal Interface

```bash
python main.py
```

---

## API

```bash
python -m uvicorn api:app --reload
```

API documentation:

```
http://127.0.0.1:8000/docs
```

---

## Tests

```bash
python -m pytest tests/test_produtos.py -v
```

---

# Technologies Used

- **Python 3.14** - Main programming language
- **FastAPI** - REST API framework
- **SQLite3** - Database system
- **Pydantic** - Data validation
- **Pytest** - Automated testing framework
- **Uvicorn** - ASGI server
- **Git** - Version control

---

# Technical Decisions

## SQLite Instead of JSON Storage

The project initially used JSON files for data storage.

SQLite was introduced to provide:

- Better data organization
- Structured queries
- More reliable persistence
- A database-based architecture

---

## Separation of Responsibilities

The project separates different responsibilities:

- Interface logic is handled by `menu.py`
- Business logic is handled by product functions
- Database operations are centralized in `database.py`
- API logic is isolated in `api.py`

This structure improves readability and makes future maintenance easier.

---

## Modular Architecture

Each module has a specific purpose, reducing code duplication and making the system easier to expand.

Future improvements can be added without requiring major changes to the existing structure.