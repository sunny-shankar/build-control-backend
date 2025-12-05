from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.common.schemas import ApiResponse


def register_exception_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        envelope = ApiResponse(
            success=False,
            message=str(exc.detail),
            data=None,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        envelope = ApiResponse(
            success=False,
            message=str(exc),
            data=None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=envelope.model_dump(),
        )
