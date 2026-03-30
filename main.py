from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import create_tables
from app.api.router import api_router

# uvicorn main:app --reload

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    create_tables()
    yield
    # Shutdown: nothing to clean up for SQLite


def create_app(  ) -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A platform to create, manage, and interact with AI agents "
            "via text and voice using OpenAI APIs."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
