from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.common.exceptions import register_exception_handlers
from app.common.schemas import ApiResponse
from app.core import settings
from app.router.api import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Build Control Backend",
        version=settings.APP_VERSION,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=settings.CORS_HEADERS,
    )

    register_exception_handlers(app)
    app.include_router(router=router)
    return app


app = create_app()


@app.get("/health", tags=["Health"], response_model=ApiResponse)
async def health_check():
    """Health check endpoint."""
    return ApiResponse(
        data={"status": "ok"},
    )
