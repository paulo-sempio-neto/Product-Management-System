# Project Structure - Product Management System

## Overview

The Product Management System is a Python project with two user-facing
interfaces:

- An interactive terminal interface
- A REST API built with FastAPI

Both interfaces use the same product service for business rules. The service
coordinates persistence through `ProductRepository`, with a default SQLite adapter.

## Repository Layout Overview

```text
Product-Management-System/
├── assets/
│   └── product-management-demo.gif
├── schemas/
│   ├── __init__.py
│   ├── error.py
│   └── product.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_api_readiness.py
│   ├── test_cli.py
│   ├── test_cli_input.py
│   ├── test_config.py
│   ├── test_database_reliability.py
│   ├── test_product_service.py
│   ├── test_product_update.py
│   └── test_products.py
├── .gitignore
├── .env.example
├── .github/workflows/ci.yml
├── api.py
├── api_errors.py
├── cli.py
├── cli_input.py
├── constants.py
├── config.py
├── database.py
├── main.py
├── product_service.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── requirements-dev.txt
└── STRUCTURE.md
```

The tree is a high-level view; the responsibility table below also covers the
configuration, repository, migration, Docker, and CI files that complete the
current architecture.

SQLite database files may be created locally during application or test
execution. They are runtime data and are ignored by Git, so they are not part of
the tracked repository layout.

## Files and Responsibilities

| Path | Current responsibility |
|---|---|
| `main.py` | CLI entry point. Calls `cli.show_menu()` when executed directly. |
| `api.py` | Provides `create_app` with repository injection and the compatible `app` entry point; maps service outcomes to HTTP and initializes storage during lifespan. |
| `cli.py` | Implements the interactive terminal menu and formats product-service results for terminal users. |
| `cli_input.py` | Parses and validates terminal input for prices, names, IDs, and menu options. |
| `database.py` | Manages SQLite connections and implements table creation, queries, and persistence. |
| `persistence.py` | Defines backend-neutral product types, persistence failures, and the repository protocol. |
| `repositories.py` | Selects a repository from validated backend settings, snapshots its connection configuration, and adapts the established SQLite functions. |
| `migrations.py` | Inspects schema state and performs explicit transactional SQLite upgrades. |
| `docs/database-evolution.md` | Migration operations, modeling decisions, and future PostgreSQL compatibility requirements. |
| `tests/test_migrations.py` | Exercises upgrades, constraint enforcement, refusal paths, and rollback. |
| `tests/test_repository_contract.py` | Verifies service injection and the backend-parametrized repository contract. |
| `tests/test_composition.py` | Verifies backend selection, configuration snapshots, repository injection, and independent application instances. |
| `product_service.py` | Implements shared product normalization, validation, duplicate checks, missing-product handling, CRUD coordination, paginated listing, search, and price reports. |
| `constants.py` | Stores CLI menu labels, prompts, validation messages, success messages, and error messages in Portuguese. |
| `schemas/product.py` | Defines the Pydantic creation, update, and response models used by the API. |
| `schemas/__init__.py` | Marks `schemas` as a Python package. |
| `tests/conftest.py` | Configures test imports and supplies isolated temporary SQLite databases and lifespan-aware API clients. |
| `tests/test_api.py` | Tests application lifespan and the main HTTP routes, validation responses, duplicate handling, search, and not-found responses. |
| `tests/test_cli.py` | Tests that CLI workflows preserve terminal behavior while using the service layer. |
| `tests/test_product_service.py` | Tests shared product rules and translation of database failures. |
| `tests/test_product_update.py` | Tests API product-name conflict behavior during updates using a temporary database. |
| `tests/test_products.py` | Tests database lookup by ID/name and service-level partial-name filtering. |
| `requirements.txt` | Lists the pinned direct Python dependencies used by the current verified environment. |
| `.gitignore` | Excludes local environments, caches, environment files, and SQLite database files from version control. |
| `Dockerfile` | Builds the unprivileged production API image with its SQLite data path at `/data/products.db`. |
| `compose.yaml` | Defines the local production-shaped API service, health check, and persistent named SQLite volume. |

## Current Data Flow

### Terminal Application

```text
main.py
  └── cli.py
        ├── cli_input.py        (terminal input parsing and validation)
        ├── constants.py        (terminal text)
        └── product_service.py  (business rules)
              └── ProductRepository (persistence.py)
                    └── SQLiteProductRepository (repositories.py)
                          └── database.py → SQLite
```

The CLI initializes products through the service when `show_menu()` starts.
Workflow functions call the service and do not execute database operations.

### REST API

```text
api.py
  ├── schemas/product.py  (request and response validation)
  └── product_service.py  (business rules)
        └── ProductRepository (persistence.py)
              └── SQLiteProductRepository (repositories.py)
                    └── database.py → configured SQLite database
```

The API factory resolves `DB_BACKEND` and `DB_NAME` through validated settings;
SQLite and `produtos.db` remain the development defaults. Its repository is fixed
for that application instance and injected into routes through a dependency.
Importing `api.py` does not access SQLite. Fresh storage is initialized when
the FastAPI lifespan starts; legacy storage requires an explicit migration first.
Routes call the product service through the unchanged public functions.
`GET /products` returns a paginated envelope with `items`, `page`, `limit`, and
`total`, and accepts an optional `name` filter. The compatibility
`/products/search/` route still returns a plain list.

### Automated Tests

```text
tests/
  ├── FastAPI TestClient ──> api.py
  ├── service tests ───────> product_service.py
  ├── CLI tests ───────────> cli.py
  └── database tests ──────> database.py
                               └── temporary SQLite databases
```

Shared repository and API tests use the `product_repository` fixture, parametrized
with `sqlite` today. Future adapters can add an isolated backend fixture and join
that contract suite. SQLite migration and file tests retain explicit SQLite
fixtures. API clients enter the lifespan of their own application instance, so
tests do not share product data or write repository database files.

## Interface Boundaries

The CLI and API share `product_service.py` for product rules:

- Names are trimmed while preserving their casing.
- Empty names and non-positive, non-finite, or non-cent prices are rejected.
- Duplicate names and missing products use explicit service errors.
- The API maps service errors to HTTP responses.
- The CLI maps service results and errors to Portuguese terminal messages.

Pydantic still validates API request shapes at the HTTP boundary, while
`cli_input.py` validates interactive input at the terminal boundary.

## Database

`database.py` uses Python's built-in `sqlite3` module. The `products` table keeps
an integer autoincrement primary key, an exactly unique text name, and an integer
`price_cents` value. Revision 2 stores money as cents with named checks for
nonblank text names and positive integer-cent prices. The immutable revision DDLs
are in `migrations.py`; the SQLite `user_version` header records its revision. See
[Database evolution](docs/database-evolution.md) for upgrade and modeling details.

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

## Engineering Quality

| Path | Responsibility |
|---|---|
| `pyproject.toml` | Configures Ruff, strict mypy checking for application modules, pytest discovery, and coverage reporting. |
| `requirements-dev.txt` | Pins Ruff 0.16.8, mypy 2.3.1, and pytest-cov 7.1.0 while including `requirements.txt`. |
| `.github/workflows/ci.yml` | Installs development dependencies, then runs formatting, linting, type checks, and pytest coverage on pushes and pull requests. |

Ruff checks formatting and common Python defects. Mypy strictly checks the
application modules. Pytest-cov reports line and branch coverage so coverage
gaps can guide meaningful future tests.

## Production Readiness Boundaries

`config.py` is shared by API and CLI/database operations. It validates process
environment settings with Pydantic without an additional settings dependency.
Testing and production require an explicit SQLite path; development keeps the
original `produtos.db` default. `DB_BACKEND` explicitly selects storage and rejects
unsupported backends; only `sqlite` is implemented. API documentation is disabled by default in
production. See README for variables and startup examples.

`api_errors.py` registers framework, request-validation, persistence, and generic
exception handlers. Existing `detail` responses remain available with an added
`error.code`; validation errors omit submitted data and internal exception context.
`schemas/error.py` documents this contract in OpenAPI. Product routes stay in
`api.py` because their size does not yet justify a router package.

The `/live` route verifies that the HTTP process is serving without using storage.
The `/health` route calls the service, which calls a read-only database readiness
probe. The database context owns commit/rollback and connection closure. All SQL
for CRUD and paginated listing stays in `database.py`, with versioned DDL in
`migrations.py`. Listing pages use SQL `COUNT`, `LIMIT`, and `OFFSET` instead of
loading every product when the API only needs one page. Write row counts detect
products removed after a service lookup, and only unique-name failures translate
to duplicate-product errors.

The new configuration, readiness, security, and database-reliability tests use
temporary databases. The full suite still includes every prior test. CI includes
dependency compatibility checking, and mypy/coverage include the new modules.

## Container Delivery

`Dockerfile` copies only the runtime API modules and schemas, installs the pinned
runtime dependencies, and starts Uvicorn on port 8000 as a non-root user. Its
production defaults require no source-mounted files: `APP_ENV=production`,
`DB_BACKEND=sqlite`, `DB_NAME=/data/products.db`, and disabled API docs. The writable `/data` directory
is the only application state location.

`compose.yaml` persists `/data` in the `product_data` named volume, binds the API
only to the local host by default, and uses `/health` for the container readiness
check. It is designed for one replica because SQLite writer locking and a local
volume do not support horizontally scaled API instances. CI builds this image after
the Python quality and test checks; publishing, an external reverse proxy, TLS,
and orchestrator manifests are intentionally not included.
