# FastAPI Conversion Guide

This document explains the conversion from Flask to FastAPI (v2.0 → v3.0).

## Why FastAPI?

FastAPI offers several advantages over Flask:

- **Performance**: 2-3x faster than Flask due to async support and Starlette
- **Modern Python**: Built on Python 3.8+ type hints
- **Automatic API Documentation**: Interactive docs with Swagger UI and ReDoc
- **Data Validation**: Built-in request/response validation with Pydantic
- **Async Support**: Native async/await for better concurrency
- **Type Safety**: Full type checking support with mypy
- **Standards-Based**: Based on OpenAPI and JSON Schema

## Major Changes

### 1. Framework Migration

| Aspect | Flask (v2.0) | FastAPI (v3.0) |
|--------|--------------|----------------|
| Framework | Flask 3.x | FastAPI 0.115+ |
| Server | Gunicorn/Werkzeug | Uvicorn (ASGI) |
| Routing | Blueprints | API Routers |
| Forms | WTForms | Pydantic Models |
| Authentication | Flask-Login | JWT + OAuth2 |
| Config | Class-based | Pydantic Settings |

### 2. File Structure Changes

```
Old (Flask):                    New (FastAPI):
├── src/                        ├── src/
│   ├── app.py                  │   ├── main.py          # FastAPI app
│   ├── settings.py             │   ├── config.py        # Pydantic settings
│   ├── extensions.py           │   ├── database.py      # SQLAlchemy setup
│   ├── auth/                   │   ├── auth_utils.py    # JWT & password
│   │   ├── views.py            │   ├── schemas.py       # Pydantic models
│   │   └── forms.py            │   └── routers/         # API endpoints
│   ├── public/                 │       ├── auth.py
│   │   └── views.py            │       ├── public.py
│   └── services/               │       └── services.py
│       └── views.py            
├── manage.py                   ├── run.py               # Dev server
└── requirements.txt            └── requirements.txt     # FastAPI deps
```

### 3. Configuration

#### Old (Flask - settings.py):
```python
class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('APP_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
```

#### New (FastAPI - config.py):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool = False
    SECRET_KEY: str
    DATABASE_URL: str = "sqlite:///dev.db"
    
    class Config:
        env_file = ".env"
```

### 4. Application Setup

#### Old (Flask - app.py):
```python
from flask import Flask

def create_app(config_obj):
    app = Flask(__name__)
    app.config.from_object(config_obj)
    return app
```

#### New (FastAPI - main.py):
```python
from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(
        title="My App",
        version="3.0.0"
    )
    return app
```

### 5. Routing

#### Old (Flask):
```python
from flask import Blueprint, jsonify

blueprint = Blueprint('auth', __name__)

@blueprint.route('/login', methods=['POST'])
def login():
    return jsonify({"message": "Logged in"})
```

#### New (FastAPI):
```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/login")
async def login(credentials: LoginSchema):
    return {"message": "Logged in"}
```

### 6. Forms → Pydantic Schemas

#### Old (WTForms):
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, InputRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
```

#### New (Pydantic):
```python
from pydantic import BaseModel, EmailStr, Field

class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
```

### 7. Authentication

#### Old (Flask-Login):
```python
from flask_login import login_user, current_user, login_required

@app.route('/protected')
@login_required
def protected():
    return f"Hello {current_user.username}"
```

#### New (FastAPI JWT):
```python
from fastapi import Depends
from .auth_utils import get_current_user

@router.get("/protected")
async def protected(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

### 8. Database Sessions

#### Old (Flask):
```python
from .data.database import db

@app.route('/users')
def get_users():
    users = db.session.query(User).all()
    return jsonify([u.to_dict() for u in users])
```

#### New (FastAPI):
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

## Running the Application

### Development

```bash
# Old (Flask)
./manage.py runserver

# New (FastAPI)
./run.py --reload
# or
uvicorn src.main:app --reload
```

### Production

```bash
# Old (Flask + Gunicorn)
gunicorn 'src.app:create_app(src.settings.app_config)'

# New (FastAPI + Uvicorn)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
# or with Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Testing

### Old (Flask + WebTest):
```python
def test_login(client):
    response = client.post('/auth/login', {
        'email': 'test@example.com',
        'password': 'password'
    })
    assert response.status_code == 200
```

### New (FastAPI + httpx):
```python
from fastapi.testclient import TestClient

def test_login(client: TestClient):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 200
```

## Environment Variables

The `.env` file format remains similar:

```bash
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://user:pass@host/db

# Optional
APP_ENV=dev
DEBUG=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

## Benefits of the Migration

1. **Better Performance**: Async support for I/O-bound operations
2. **Type Safety**: Full type checking with mypy
3. **Auto Documentation**: Always up-to-date API docs
4. **Modern Ecosystem**: Compatible with modern Python tools
5. **Better Testing**: Built-in test client
6. **Standards Compliance**: OpenAPI/JSON Schema
7. **Easier API Development**: Pydantic validation

## Migration Checklist

- [x] Update dependencies (Flask → FastAPI)
- [x] Create FastAPI application structure
- [x] Convert configuration to Pydantic Settings
- [x] Set up JWT authentication
- [x] Create Pydantic schemas
- [x] Create example auth router
- [ ] Convert all Flask routes to FastAPI routers
- [ ] Update templates (if using server-side rendering)
- [ ] Convert tests to use FastAPI TestClient
- [ ] Update documentation

## Common Pitfalls

1. **Async/Sync**: Remember FastAPI endpoints can be async or sync
2. **Dependency Injection**: Use `Depends()` for database sessions
3. **Response Models**: Define Pydantic response models for validation
4. **CORS**: Don't forget to configure CORS for frontend apps
5. **Static Files**: Mount static files if serving assets

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
