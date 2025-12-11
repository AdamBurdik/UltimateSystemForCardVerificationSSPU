"""
Authentication routes - rendering HTML pages with forms
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from ..config import settings
from ..database import get_db
from ..data.models import User
from ..auth_utils import get_password_hash, verify_password

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


class FlashMessage:
    """Helper class to handle flash messages"""
    @staticmethod
    def add(request: Request, message: str, category: str = "info"):
        if "flash_messages" not in request.session:
            request.session["flash_messages"] = []
        request.session["flash_messages"].append({"message": message, "category": category})

    @staticmethod
    def get(request: Request):
        messages = request.session.pop("flash_messages", [])
        return messages


def get_current_user_from_session(request: Request, db: Session):
    """Get current user from session if exists"""
    user_id = request.session.get("user_id")
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    return None


class AnonymousUser:
    """Mock anonymous user object"""
    def is_anonymous(self):
        return True
    def is_verified(self):
        return False
    @property
    def access(self):
        return None


class MockForm:
    """Mock form object for templates"""
    def __init__(self):
        self.email = MockField(name="email", label="Email")
        self.password = MockField(name="password", label="Password")
        self.username = MockField(name="username", label="Username")
        self.remember_me = MockField(name="remember_me", label="Remember me")
        self.csrf_token = MockField(name="csrf_token", label="")

    def hidden_tag(self):
        return ''


class MockField:
    """Mock form field"""
    def __init__(self, name: str, label: str = "", data: str = ""):
        self.name = name
        self.label = label or name.capitalize()
        self.data = data
        self.errors = []


def get_template_context(request: Request, db: Session, **kwargs):
    """Helper to create standard template context with get_flashed_messages"""
    user = get_current_user_from_session(request, db) or AnonymousUser()

    # Get flash messages but don't clear them yet - let template decide
    flash_messages_store = request.session.get("flash_messages", [])

    def get_flashed_messages_func(with_categories=False):
        # Clear messages on first call
        messages = request.session.pop("flash_messages", [])
        if with_categories:
            return [(msg["category"], msg["message"]) for msg in messages]
        return [msg["message"] for msg in messages]

    context = {
        "request": request,
        "user": user,
        "current_user": user,
        "get_flashed_messages": get_flashed_messages_func
    }
    context.update(kwargs)
    return context


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Display login form"""
    form = MockForm()
    context = get_template_context(request, db, form=form)
    return templates.TemplateResponse("auth/login.tmpl", context)


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember_me: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    user = db.query(User).filter(User.email == email).first()

    # Use verify_password function from auth_utils
    if user and verify_password(password, user.password):
        # Store user ID in session
        request.session["user_id"] = user.id
        FlashMessage.add(request, "Logged in successfully", "info")
        return RedirectResponse(url="/", status_code=303)
    else:
        FlashMessage.add(request, "Invalid email/password combination", "danger")
        return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    request.session.pop("user_id", None)
    FlashMessage.add(request, "Logged out successfully", "info")
    return RedirectResponse(url="/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    """Display registration form"""
    form = MockForm()
    context = get_template_context(request, db, form=form)
    return templates.TemplateResponse("auth/register.tmpl", context)


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration form submission"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        FlashMessage.add(request, "Jméno už je obsazeno", "warning")
        return RedirectResponse(url="/auth/register", status_code=303)

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        FlashMessage.add(request, "Tento e-mail už používá jiný uživatel", "warning")
        return RedirectResponse(url="/auth/register", status_code=303)

    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log in the new user
    request.session["user_id"] = new_user.id

    FlashMessage.add(request, f"Thanks for signing up {username}. Welcome!", "info")
    return RedirectResponse(url="/", status_code=303)


@router.get("/account", response_class=HTMLResponse)
async def account_page(request: Request, db: Session = Depends(get_db)):
    """Display account management page"""
    user = get_current_user_from_session(request, db)
    if not user:
        FlashMessage.add(request, "Please log in to access this page", "warning")
        return RedirectResponse(url="/auth/login", status_code=303)

    form = MockForm()
    form.username.data = user.username
    form.email.data = user.email

    context = get_template_context(request, db, form=form)
    return templates.TemplateResponse("auth/editAccountAdmin.tmpl", context)


@router.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password_page(request: Request, db: Session = Depends(get_db)):
    """Display forgot password form"""
    form = MockForm()
    context = get_template_context(request, db, form=form)
    return templates.TemplateResponse("auth/forgot_password.tmpl", context)
