from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from .config import settings
from .database import engine, Base

# Import routers
from .routers import auth


def create_app() -> FastAPI:
    """
    Application factory for creating FastAPI app instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    if os.path.exists(settings.STATIC_DIR):
        app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    
    # Register routers
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    # app.include_router(public.router, prefix="", tags=["public"])
    # app.include_router(services.router, prefix="/services", tags=["services"])
    
    # Create database tables (in production, use Alembic migrations)
    @app.on_event("startup")
    async def startup():
        # Create tables if they don't exist
        # In production, comment this out and use: alembic upgrade head
        if settings.DEBUG:
            Base.metadata.create_all(bind=engine)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": os.getenv("APP_ENV", "dev")
        }
    
    return app


# Create app instance
app = create_app()
