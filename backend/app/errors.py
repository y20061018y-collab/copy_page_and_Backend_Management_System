from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def api_error(code: str, message: str, status_code: int, details: object | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "details": {} if details is None else details})


async def http_error_handler(_: Request, exception: HTTPException) -> JSONResponse:
    if isinstance(exception.detail, dict) and {"code", "message"} <= exception.detail.keys():
        return api_error(
            exception.detail["code"],
            exception.detail["message"],
            exception.status_code,
            exception.detail.get("details"),
        )

    code = {
        401: "AUTH_REQUIRED",
        404: "NOT_FOUND",
        409: "CONFLICT",
        413: "UPLOAD_TOO_LARGE",
        422: "VALIDATION_ERROR",
    }.get(exception.status_code, "REQUEST_ERROR")
    return api_error(code, str(exception.detail), exception.status_code)


async def validation_error_handler(_: Request, exception: RequestValidationError) -> JSONResponse:
    return api_error("VALIDATION_ERROR", "请求数据无效", 422, exception.errors())
