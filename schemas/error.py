"""Public error contract; the legacy detail field remains available."""

from pydantic import BaseModel


class ValidationIssue(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ErrorInfo(BaseModel):
    code: str


class ErrorResponse(BaseModel):
    detail: str | list[ValidationIssue]
    error: ErrorInfo
