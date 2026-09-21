"""Consistent public errors without leaking request data or internal exceptions."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from product_service import ProductPersistenceError, ProductValidationError

logger = logging.getLogger(__name__)


def error_response(status: int, detail: object, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"detail": detail, "error": {"code": code}},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        try:
            code = HTTPStatus(exc.status_code).name.lower()
        except ValueError:
            code = "http_error"
        if exc.status_code == 422:
            code = "validation_error"
        response = error_response(exc.status_code, exc.detail, code)
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Keep FastAPI's detail list but omit input and ctx (potential secrets,
        # non-JSON values, and exception objects).
        details = [
            {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        return error_response(422, details, "validation_error")

    @app.exception_handler(ProductValidationError)
    async def invalid_product(
        _request: Request, exc: ProductValidationError
    ) -> JSONResponse:
        return error_response(422, str(exc), "validation_error")

    @app.exception_handler(ProductPersistenceError)
    async def persistence_failure(
        _request: Request, _exc: ProductPersistenceError
    ) -> JSONResponse:
        logger.error("Product persistence operation failed")
        return error_response(
            500, "Erro interno ao acessar os produtos", "internal_server_error"
        )

    @app.exception_handler(Exception)
    async def unexpected_failure(_request: Request, _exc: Exception) -> JSONResponse:
        logger.error("Unhandled application error (%s)", type(_exc).__name__)
        return error_response(500, "Erro interno do servidor", "internal_server_error")
