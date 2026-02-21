from fastapi import FastAPI
from api.routes import router
from api.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-agent orchestration system for AI-powered code generation and review"
    )

    app.include_router(router)

    return app


app = create_app()
