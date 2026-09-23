from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, cast

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request

from api_errors import register_error_handlers
from config import Settings, get_settings
from persistence import ProductRepository
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
from repositories import get_repository
from schemas.error import ErrorResponse
from schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


def get_product_repository(request: Request) -> ProductRepository:
    return cast(ProductRepository, request.app.state.product_repository)


ProductStorage = Annotated[ProductRepository, Depends(get_product_repository)]


def create_app(
    settings: Settings | None = None, *, repository: ProductRepository | None = None
) -> FastAPI:
    """Compose an independent application; database I/O begins only at startup."""
    resolved = settings if settings is not None else get_settings()
    storage = (
        repository if repository is not None else get_repository(settings=resolved)
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        initialize_products(repository=storage)
        yield

    application = FastAPI(
        title="Sistema de Produtos API",
        description="API para gerenciamento de produtos",
        version="1.0.0",
        lifespan=lifespan,
        debug=False,
        docs_url="/docs" if resolved.docs_enabled else None,
        redoc_url="/redoc" if resolved.docs_enabled else None,
        openapi_url="/openapi.json" if resolved.docs_enabled else None,
        summary="Product CRUD with a shared API/CLI service and SQLite persistence",
        responses={
            status: {"model": ErrorResponse}
            for status in (400, 404, 405, 409, 422, 500, 503)
        },
        openapi_tags=[
            {"name": "products", "description": "Product management and name search"},
            {"name": "system", "description": "Service information and readiness"},
        ],
    )
    application.state.product_repository = storage
    register_error_handlers(application)
    application.include_router(router)
    return application


@router.get(
    "/health", tags=["system"], responses={503: {"description": "Storage unavailable"}}
)
def health(repository: ProductStorage) -> dict[str, str]:
    """Readiness check: verifies the existing products table without writing."""
    try:
        check_product_storage(repository=repository)
    except ProductPersistenceError as exc:
        raise HTTPException(503, "Serviço indisponível") from exc
    return {"status": "ok"}


@router.get("/live", tags=["system"])
def live() -> dict[str, str]:
    """Liveness check: confirms the HTTP application can serve requests."""
    return {"status": "ok"}


@router.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": "Bem-vindo à API de Produtos!"}


@router.get("/products", response_model=list[ProductResponse], tags=["products"])
def list_all_products(repository: ProductStorage) -> list[Product]:
    """Retorna todos os produtos"""
    return list_products(repository=repository)


@router.get(
    "/products/search/",
    response_model=list[ProductResponse],
    tags=["products"],
)
def search_products(name: str, repository: ProductStorage) -> list[Product]:
    """Busca produtos por parte do nome"""
    return search_products_service(name, repository=repository)


@router.get("/products/{product_id}", response_model=ProductResponse, tags=["products"])
def get_product(product_id: int, repository: ProductStorage) -> Product:
    """Retorna um produto pelo ID"""
    try:
        return get_product_service(product_id, repository=repository)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        ) from exc


@router.post(
    "/products", response_model=ProductResponse, status_code=201, tags=["products"]
)
def create_product(product: ProductCreate, repository: ProductStorage) -> Product:
    """Cria um novo produto"""
    try:
        return create_product_service(
            product.name, product.price, repository=repository
        )
    except DuplicateProductError as exc:
        raise HTTPException(
            status_code=409,
            detail="Produto já cadastrado",
        ) from exc
    except ProductValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.put("/products/{product_id}", response_model=ProductResponse, tags=["products"])
def update_product(
    product_id: int,
    product: ProductUpdate,
    repository: ProductStorage,
) -> Product:
    try:
        return update_product_service(
            product_id,
            product.name,
            product.price,
            repository=repository,
        )
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        ) from exc
    except DuplicateProductError as exc:
        raise HTTPException(
            status_code=409,
            detail="Já existe outro produto com esse nome",
        ) from exc
    except ProductValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/products/{product_id}", status_code=204, tags=["products"])
def delete_product(product_id: int, repository: ProductStorage) -> None:
    try:
        delete_product_service(product_id, repository=repository)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        ) from exc


# Retain the existing uvicorn api:app entry point.
app = create_app()
