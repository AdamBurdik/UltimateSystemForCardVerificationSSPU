"""
Public routes - rendering HTML pages
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from ..config import settings
from ..database import get_db

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


def get_current_user_from_session(request: Request, db: Session):
    """Get current user from session if exists (pass db explicitly)"""
    user_id = request.session.get("user_id")
    if user_id:
        from ..data.models import User
        user = db.query(User).filter(User.id == user_id).first()
        return user
    return None


def get_flashed_messages(request: Request, with_categories=False):
    """Get flash messages from session"""
    messages = request.session.pop("flash_messages", [])
    if with_categories:
        return [(msg["category"], msg["message"]) for msg in messages]
    return [msg["message"] for msg in messages]


# Remove the broken template global registration
# templates.env.globals['get_flashed_messages'] = get_flashed_messages


class AnonymousUser:
    """Mock anonymous user object"""
    def is_anonymous(self):
        return True
    def is_verified(self):
        return False


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Homepage"""
    user = get_current_user_from_session(request, db)
    current_user = user if user else AnonymousUser()

    # Helper function for templates
    def get_flashed_messages_func(with_categories=False):
        return get_flashed_messages(request, with_categories)

    return templates.TemplateResponse(
        "public/index.tmpl",
        {
            "request": request,
            "current_user": current_user,
            "user": user,
            "get_flashed_messages": get_flashed_messages_func
        }
    )


@router.get("/favicon.ico")
async def favicon():
    """Favicon endpoint"""
    favicon_path = os.path.join(settings.STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"message": "Favicon not found"}
