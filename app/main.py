from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.common.exceptions import register_exception_handlers
from app.core.config import settings


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

    return app


app = create_app()
