from fastapi import Request
from fastapi.responses import JSONResponse


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    print(f"Error: {exc}")

    if hasattr(exc, "code"):
        code = exc.code
    else:
        code = "INTERNAL_ERROR"

    status_map = {
        "INVALID_PARAMS": 400,
        "SEARXNG_UNAVAILABLE": 503,
        "REQUEST_TIMEOUT": 504,
        "INTERNAL_ERROR": 500,
    }
    status = status_map.get(code, 500)

    msg_map = {
        "INVALID_PARAMS": "参数缺失或格式错误",
        "SEARXNG_UNAVAILABLE": "搜索引擎服务不可用",
        "REQUEST_TIMEOUT": "请求超时",
        "INTERNAL_ERROR": "内部错误",
    }

    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": str(exc) if str(exc) else msg_map.get(code, "未知错误")
            }
        }
    )
