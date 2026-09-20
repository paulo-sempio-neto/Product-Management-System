# Project Structure - Product Management System

## Overview

The Product Management System is a Python project with two user-facing
interfaces:

- An interactive terminal interface
- A REST API built with FastAPI

Both interfaces use the same SQLite data-access module, but they currently
implement their interface-specific workflows separately. There is not yet a
shared business-service layer between the CLI and API.

## Repository Layout

```text
Product-Management-System/
├── assets/
│   └── product-management-demo.gif
├── schemas/
│   ├── __init__.py
│   └── product.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_product_update.py
│   └── test_products.py
├── .gitignore
├── api.py
├── cli.py
├── constants.py
├── database.py
├── main.py
├── product_service.py
├── README.md
├── requirements.txt
└── STRUCTURE.md
```

SQLite database files may be created locally during application or test
execution. They are runtime data and are ignored by Git, so they are not part of
the tracked repository layout.

## Files and Responsibilities

| Path | Current responsibility |
|---|---|
| `main.py` | CLI entry point. Calls `cli.show_menu()` when executed directly. |
| `api.py` | Creates the FastAPI application, initializes its configured SQLite database, and defines HTTP routes for product CRUD and partial-name search. |
| `cli.py` | Implements the interactive terminal menu and its product workflows, including CRUD, listing, search, average price, and minimum-price filtering. |
| `database.py` | Creates SQLite connections and the `products` table, and implements product persistence, lookup, and filtering functions. |
| `product_service.py` | Contains CLI input parsing and validation helpers for prices, names, IDs, and menu options. It is not currently a shared API/CLI service layer. |
| `constants.py` | Stores CLI menu labels, prompts, validation messages, success messages, and error messages in Portuguese. |
| `schemas/product.py` | Defines the Pydantic creation, update, and response models used by the API. |
| `schemas/__init__.py` | Marks `schemas` as a Python package. |
| `tests/conftest.py` | Configures test imports and supplies a temporary SQLite database fixture for database-level tests. |
| `tests/test_api.py` | Tests the main HTTP routes, validation responses, duplicate handling, search, and not-found responses. |
| `tests/test_product_update.py` | Tests API product-name conflict behavior during updates using a temporary database. |
| `tests/test_products.py` | Tests database lookup by ID/name and partial-name filtering. |
| `requirements.txt` | Lists the pinned direct Python dependencies used by the current verified environment. |
| `.gitignore` | Excludes local environments, caches, environment files, and SQLite database files from version control. |

## Current Data Flow

### Terminal Application

```text
main.py
  └── cli.py
        ├── product_service.py  (terminal input parsing and validation)
        ├── constants.py        (terminal text)
        └── database.py
              └── local SQLite database
```

The CLI initializes the database table when `show_menu()` starts. Its workflow
functions call `database.py` directly.

### REST API

```text
api.py
  ├── schemas/product.py  (request and response validation)
  └── database.py
        └── configured SQLite database
```

The API initializes its database when `api.py` is imported. It reads the
`DB_NAME` environment variable when present and otherwise uses `produtos.db`.
API route functions call `database.py` directly.

### Automated Tests

```text
tests/
  ├── FastAPI TestClient ──> api.py
  └── database tests ──────> database.py
                               └── test SQLite databases
```

The database lookup tests and product-update conflict test use pytest temporary
directories. The main API test module currently uses the separate local
`test_api.db` file and changes `api.DB_NAME` for its test operations.

## Interface Boundaries

The CLI and API share the SQLite functions in `database.py`, but their
validation and workflow rules are not centralized:

- The CLI uses `product_service.py` for terminal input validation.
- The API uses the Pydantic models in `schemas/product.py`.
- The CLI and API each handle product existence and duplicate checks in their
  own workflow functions.

This describes the current implementation. Introducing a shared domain or
business-service layer is a possible future change, not part of the present
architecture.

## Database

`database.py` uses Python's built-in `sqlite3` module. It creates one table:

```sql
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL
);
```

The default application database is `produtos.db`. Local `.db`, `.sqlite`,
and `.sqlite3` files are ignored and should not be committed.

## Running the Project

The canonical local virtual environment directory is `.venv`.

### CLI

```powershell
.\.venv\Scripts\python.exe main.py
```

### API

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Tests

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

## Current Technology Baseline

- Python 3.14.3
- FastAPI 0.141.1
- Uvicorn 0.52.4
- Pydantic 2.13.5
- Pytest 9.1.1
- HTTPX 0.28.1
- SQLite through Python's standard library
