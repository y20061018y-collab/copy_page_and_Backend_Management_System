from fastapi import Request
from fastapi.responses import JSONResponse


def api_error(code: str, message: str, status_code: int, details: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "details": details or {}})


async def http_error_handler(_: Request, exception: Exception) -> JSONResponse:
    return api_error("REQUEST_ERROR", str(exception), 500)
