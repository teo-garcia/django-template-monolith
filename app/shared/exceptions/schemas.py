from typing import Any

from ninja import Schema
from pydantic import Field


class ErrorMeta(Schema):
    requestId: str  # noqa: N815


class ErrorEnvelope(Schema):
    success: bool = False
    statusCode: int = Field(..., ge=400)  # noqa: N815
    timestamp: str
    path: str
    method: str
    message: str | list[str]
    error: str
    errors: Any | None = None
    meta: ErrorMeta | None = None
