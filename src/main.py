from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
    
    # Setup Jinja2 templates
    templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
    
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
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint - returns HTML homepage"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{settings.APP_NAME}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #333; }}
                .info {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .links {{ margin-top: 20px; }}
                a {{ color: #0066cc; text-decoration: none; margin-right: 20px; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎫 {settings.APP_NAME}</h1>
                <p>Version: <strong>{settings.APP_VERSION}</strong></p>
                
                <div class="info">
                    <h2>Welcome!</h2>
                    <p>This is the Ultimate System for Card Verification.</p>
                    <p>Status: ✅ Running</p>
                </div>
                
                <div class="links">
                    <h3>Available Resources:</h3>
                    <a href="/api/docs">📚 API Documentation (Swagger)</a><br/>
                    <a href="/api/redoc">📖 API ReDoc</a><br/>
                    <a href="/health">💚 Health Check</a><br/>
                    <a href="/auth">🔐 Authentication</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
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
