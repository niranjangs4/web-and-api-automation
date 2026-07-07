from __future__ import annotations

from dataclasses import dataclass


@dataclass
class APIResponse:
    status_code: int
    body: dict
    headers: dict


class BaseAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def synthetic_get(self, path: str, *, authorized: bool = True, correlation_id: str | None = None) -> APIResponse:
        headers = {}
        if correlation_id:
            headers["x-correlation-id"] = correlation_id
        if not authorized:
            return APIResponse(status_code=401, body={"detail": "Unauthorized"}, headers=headers)
        return APIResponse(status_code=200, body={"status": "ok", "path": path}, headers=headers)

    def synthetic_post(self, path: str, payload: dict, *, idempotency_key: str | None = None) -> APIResponse:
        if "requiredName" not in payload:
            return APIResponse(status_code=422, body={"field": "requiredName", "error": "missing"}, headers={})
        if not isinstance(payload.get("requiredName"), str):
            return APIResponse(status_code=422, body={"field": "requiredName", "error": "invalid_type"}, headers={})
        headers = {"idempotency-key": idempotency_key or ""}
        return APIResponse(status_code=201, body={"id": "res_001", "created": True}, headers=headers)
