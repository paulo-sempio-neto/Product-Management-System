from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from api_errors import register_error_handlers
from config import get_settings
from product_service import (
    DuplicateProductError,
    Product,
    ProductNotFoundError,
    ProductPersistenceError,
    ProductValidationError,
    check_product_storage,
    initialize_products,
    list_products,
)
from product_service import (
    create_product as create_product_service,
)
from product_service import (
    delete_product as delete_product_service,
)
from product_service import (
    get_product as get_product_service,
)
from product_service import (
    search_products as search_products_service,
)
from product_service import (
    update_product as update_product_service,
)
from schemas.error import ErrorResponse
from schemas.product import ProductCreate, ProductResponse, ProductUpdate

settings = get_settings()
# Retained for compatibility with existing test fixtures and integrations.
DB_NAME = settings.database_path


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_products(DB_NAME)
    yield


app = FastAPI(
    title="Sistema de Produtos API",
    description="API para gerenciamento de produtos",
    version="1.0.0",
    lifespan=lifespan,
    debug=False,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
    summary="Product CRUD with a shared API/CLI service and SQLite persistence",
    responses={
        status: {"model": ErrorResponse} for status in (400, 404, 405, 422, 500, 503)
    },
    openapi_tags=[
        {"name": "products", "description": "Product management and name search"},
        {"name": "system", "description": "Service information and readiness"},
    ],
)
register_error_handlers(app)


@app.get(
    "/health", tags=["system"], responses={503: {"description": "Storage unavailable"}}
)
def health() -> dict[str, str]:
    """Readiness check: verifies the existing products table without writing."""
    try:
        check_product_storage(DB_NAME)
    except ProductPersistenceError as exc:
        raise HTTPException(503, "Serviço indisponível") from exc
    return {"status": "ok"}


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": "Bem-vindo à API de Produtos!"}


@app.get("/products", response_model=list[ProductResponse], tags=["products"])
def list_all_products() -> list[Product]:
    """Retorna todos os produtos"""
    return list_products(DB_NAME)


@app.get(
    "/products/search/",
    response_model=list[ProductResponse],
    tags=["products"],
)
def search_products(name: str) -> list[Product]:
    """Busca produtos por parte do nome"""
    result = search_products_service(name, DB_NAME)
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado")
    return result


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["products"])
def get_product(product_id: int) -> Product:
    """Retorna um produto pelo ID"""
    try:
        return get_product_service(product_id, DB_NAME)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        ) from exc


@app.post(
    "/products", response_model=ProductResponse, status_code=201, tags=["products"]
)
def create_product(product: ProductCreate) -> Product:
    """Cria um novo produto"""
    try:
        return create_product_service(product.name, product.price, DB_NAME)
    except DuplicateProductError as exc:
        raise HTTPException(
            status_code=400,
            detail="Produto já cadastrado",
        ) from exc
    except ProductValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.put("/products/{product_id}", response_model=ProductResponse, tags=["products"])
def update_product(
    product_id: int,
    product: ProductUpdate,
) -> Product:
    try:
        return update_product_service(
            product_id,
            product.name,
            product.price,
            DB_NAME,
        )
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        ) from exc
    except DuplicateProductError as exc:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro produto com esse nome",
        ) from exc
    except ProductValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.delete("/products/{product_id}", status_code=204, tags=["products"])
def delete_product(product_id: int) -> None:
    try:
        delete_product_service(product_id, DB_NAME)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        ) from exc
