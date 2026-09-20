# 📦 Product Management System

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
![Pytest](https://img.shields.io/badge/Pytest-Testing-yellow)

A product management project built with Python, FastAPI, and SQLite. It provides
an interactive terminal interface and an HTTP API for managing products.

This is a learning and portfolio project for practicing backend development,
database integration, CRUD operations, validation, project organization, and
automated testing. It is not presented as a production-ready system.

## 🎬 Quick Demo

<p align="center">
  <img
    src="./assets/product-management-demo.gif"
    alt="Product Management System demonstration"
    width="100%"
  />
</p>

## 🚀 Current Features

- Product creation, listing, lookup, update, and deletion
- REST API built with FastAPI
- Interactive terminal interface in Portuguese
- SQLite persistence
- Exact ID lookup and partial-name search
- CLI reports for average price and products above a minimum price
- Request validation with Pydantic
- Automated tests with Pytest

## 🛠 Technologies

- Python 3.14
- FastAPI
- SQLite
- Pydantic
- Uvicorn
- Pytest
- HTTPX for API tests

The current development baseline uses **Python 3.14.3**. Use Python 3.14.3 to
reproduce the verified local environment.

## 🌎 Language

The application interface is currently available in Portuguese. Project
documentation and technical descriptions are written in English.

## 📂 Project Structure

```text
Product-Management-System/
├── assets/                 # Demo assets
├── schemas/                # Pydantic API models
├── tests/                  # Automated database and API tests
├── api.py                  # FastAPI application and routes
├── cli.py                  # Interactive terminal workflows
├── constants.py            # CLI labels, prompts, and messages
├── database.py             # SQLite connection and data operations
├── main.py                 # CLI entry point
├── product_service.py      # CLI input parsing and validation helpers
├── requirements.txt        # Pinned direct dependencies
├── README.md
└── STRUCTURE.md            # Detailed architecture documentation
```

See [STRUCTURE.md](STRUCTURE.md) for the current module responsibilities and
data flow.

## ⚙️ Setup

### 1. Clone and enter the repository

```powershell
git clone https://github.com/paulo-sempio-neto/Product-Management-System.git
cd Product-Management-System
```

### 2. Create the canonical virtual environment

```powershell
py -3.14 -m venv .venv
```

The canonical environment directory for this project is `.venv`.

### 3. Activate it on Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Install the pinned dependencies

```powershell
python -m pip install -r requirements.txt
```

## ▶️ Run the CLI

With `.venv` activated:

```powershell
python main.py
```

The terminal menu provides the currently implemented product-management
operations.

## 🌐 Run the API

With `.venv` activated:

```powershell
python -m uvicorn api:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 🗄 Database

The application uses SQLite. The database layer creates the `products` table
when the CLI or API initializes it.

Local runtime databases such as `produtos.db` and test databases such as
`test_api.db` are ignored by Git. They are local data files and should not be
committed.

## 🧪 Run the Tests

With `.venv` activated:

```powershell
python -B -m pytest -q -p no:cacheprovider
```

The test suite covers the current API behavior and selected database lookup and
search operations.

## 📚 Development Goals

This project is intended to demonstrate and improve:

- Python backend development
- REST API development
- SQLite integration
- CRUD design
- Input and request validation
- Automated testing
- Incremental software maintenance

## 🔮 Possible Future Improvements

- Strengthen separation between interface, business, and persistence logic
- Expand validation and database integrity rules
- Add authentication and authorization
- Add product categories and inventory information
- Create a frontend interface
- Add Docker support
- Add CI/CD automation
- Deploy the application

## 👤 Author

**Paulo Sempio Neto**

GitHub: https://github.com/paulo-sempio-neto
