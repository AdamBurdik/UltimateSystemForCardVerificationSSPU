from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse
import os

from .config import settings
from .database import engine, Base

# Import routers
from .routers import auth
from . import util  # Import utilities for Jinja2 context

# Create shared templates instance with custom url_for
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# Override url_for with our custom implementation
templates.env.globals['url_for'] = util.url_for


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
    
    # Add session middleware for template-based authentication
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
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
    # API routers (JWT authentication)
    app.include_router(auth.router, prefix="/api/auth", tags=["api-auth"])
    
    # GUI routers (session-based authentication)
    from .routers import auth_views, public_views
    # Set the shared templates instance on the routers
    public_views.templates = templates
    auth_views.templates = templates
    
    app.include_router(public_views.router, tags=["public"])
    app.include_router(auth_views.router, prefix="/auth", tags=["auth"])
    
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
