from dataclasses import dataclass
from typing import Any


@dataclass
class ApiError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {
        "data": data,
        "meta": {"request_id": request_id},
    }


def error_payload(code: str, message: str, request_id: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "meta": {"request_id": request_id},
    }