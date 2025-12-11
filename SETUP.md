# Setup Guide - FastAPI Ultimate Card Verification System

This guide will help you set up and run the Ultimate Card Verification System (FastAPI version).

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** (tested with Python 3.12)
- **Git** for cloning the repository
- **MySQL/MariaDB** (optional, SQLite is used for development)

## Step 1: Clone the Repository

```bash
git clone https://github.com/AdamBurdik/UltimateSystemForCardVerificationSSPU.git
cd UltimateSystemForCardVerificationSSPU
```

## Step 2: Create Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

## Step 3: Install Dependencies

Install the FastAPI application and all dependencies:

```bash
# Install the application in development mode
pip install -e .

# Or install with development dependencies (includes testing tools)
pip install -e ".[dev]"
```

### Manual Installation (if above fails)

If the automatic installation doesn't work, install dependencies manually:

```bash
pip install fastapi uvicorn 'pydantic[email]' pydantic-settings \
    'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart \
    sqlalchemy alembic pymysql httpx pytest pytest-asyncio
```

## Step 4: Configure Environment Variables

Create a `.env` file in the project root directory.

▼ ▼ ▼ ▼

**IMPORTANT: The `.env` file MUST be encoded in UTF-8 without BOM!**

▲ ▲ ▲ ▲

### Option 1: Using VS Code (Recommended for Windows)

1. In VS Code, create a new file `.env` in the project root
2. Add the configuration (see example below)
3. Check the encoding in the bottom-right corner of VS Code
4. If it shows anything other than "UTF-8", click it and select "Save with Encoding" → "UTF-8"

### Option 2: Using PowerShell (Windows)

```powershell
# Generate secret key and create .env file with UTF-8 encoding
$secretKey = py -c "import secrets; print(secrets.token_hex(32))"
@"
SECRET_KEY=$secretKey
DATABASE_URL=sqlite:///./dev.db
APP_ENV=dev
DEBUG=true
"@ | Out-File -FilePath .env -Encoding utf8 -NoNewline
```

### Option 3: Using Bash (Linux/macOS)

```bash
# Generate a secure secret key
python3 -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" > .env

# Add database URL (SQLite for development)
echo "DATABASE_URL=sqlite:///./dev.db" >> .env
echo "APP_ENV=dev" >> .env
echo "DEBUG=true" >> .env
```

**Full `.env` file example:**

```bash
# Required
SECRET_KEY=your-generated-secret-key-here

# Database
DATABASE_URL=sqlite:///./dev.db
# For MySQL/MariaDB:
# DATABASE_URL=******localhost/karty?charset=utf8

# Email (optional)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@example.com

# Environment
APP_ENV=dev
DEBUG=true
```

## Step 5: Initialize Database

The database will be created automatically on first run in development mode, or you can use Alembic migrations:

```bash
# Check current migration state
alembic current

# Apply migrations (if any)
alembic upgrade head

# Or create tables manually (development only)
python3 -c "from src.database import engine, Base; Base.metadata.create_all(engine)"
```

## Step 6: Run the Application

### Development Server (with auto-reload)

```bash
# Using the run.py script (Linux/macOS)
./run.py --reload

# Using the run.py script (Windows)
py run.py --reload
# Or: python run.py --reload

# Or using uvicorn directly
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

The application will be available at:

- **Application**: <http://localhost:8000>
- **API Documentation (Swagger)**: <http://localhost:8000/api/docs>
- **API Documentation (ReDoc)**: <http://localhost:8000/api/redoc>
- **Health Check**: <http://localhost:8000/health>

### Production Server

For production, use more workers and bind to all interfaces:

```bash
# Using uvicorn with multiple workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn with uvicorn workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Step 7: Test the API

### Using the Interactive API Documentation

Open <http://localhost:8000/api/docs> in your browser. You can:

1. View all available endpoints
2. Test endpoints directly from the browser
3. See request/response schemas

### Using curl (Linux/macOS)

```bash
# Health check
curl http://localhost:8000/health

# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login and get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Use the token to access protected endpoints
TOKEN="your-token-here"
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using PowerShell (Windows)

```powershell
# Health check
curl http://localhost:8000/health

# Register a new user
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/register" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# Login and get JWT token
$loginBody = @{
    username = "test@example.com"
    password = "password123"
}

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $loginBody

$token = $response.access_token

# Use the token to access protected endpoints
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/auth/me" `
  -Headers $headers
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Register a new user
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/auth/register", json=user_data)
print(response.json())

# Login and get JWT token
login_data = {
    "username": "test@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/auth/login", data=login_data)
token = response.json()["access_token"]

# Use the token to access protected endpoints
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/auth/me", headers=headers)
print(response.json())
```

## Step 8: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest test/test_fastapi_auth.py

# Run with verbose output
pytest -v
```

## Troubleshooting

### UnicodeDecodeError: 'utf-8' codec can't decode byte

This error occurs when the `.env` file is not encoded in UTF-8:

#### **Solution 1: Fix encoding in VS Code**

1. Open `.env` in VS Code
2. Click on the encoding in the bottom-right corner (e.g., "UTF-16 LE")
3. Select "Save with Encoding"
4. Choose "UTF-8" (NOT "UTF-8 with BOM")
5. Save the file

#### **Solution 2: Recreate the file**

```powershell
# Windows PowerShell - backup old file and create new one
if (Test-Path .env) { Move-Item .env .env.backup }
$secretKey = py -c "import secrets; print(secrets.token_hex(32))"
@"
SECRET_KEY=$secretKey
DATABASE_URL=sqlite:///./dev.db
APP_ENV=dev
DEBUG=true
"@ | Out-File -FilePath .env -Encoding utf8 -NoNewline
```

#### **Solution 3: Use Notepad++ (Windows)**

1. Open `.env` in Notepad++
2. Menu: Encoding → Convert to UTF-8 (NOT UTF-8 BOM)
3. Save the file

### Import Errors

If you get import errors, make sure you're in the project root and the virtual environment is activated:

```bash
# Linux/macOS
pwd  # Should show the project directory
which python  # Should show the venv python

# Windows PowerShell
Get-Location  # Should show the project directory
Get-Command python | Select-Object -ExpandProperty Source  # Should show venv python
```

### Database Errors

If you get database connection errors:

1. Check your `DATABASE_URL` in `.env`
2. For SQLite, ensure the directory is writable
3. For MySQL, ensure the database exists and credentials are correct

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
py run.py --port 8080

# Windows PowerShell - find and kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Linux/macOS - kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Email Validation Errors

If you see "email-validator not installed":

```bash
pip install 'pydantic[email]' email-validator
```

## Next Steps

1. **Explore the API**: Visit <http://localhost:8000/api/docs>
2. **Read the Documentation**: Check `FASTAPI_MIGRATION.md` and `PROJECT_SUMMARY.md`
3. **Customize**: Modify `src/config.py` for your needs
4. **Add Features**: Create new routers in `src/routers/`

## Development Workflow

### Creating a New Endpoint

1. Define Pydantic schemas in `src/schemas.py`
2. Create or update a router in `src/routers/`
3. Register the router in `src/main.py`
4. Write tests in `test/`
5. Run tests to verify

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration in migrations/versions/

# Apply the migration
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Useful Commands

```bash
# Check what's running
./run.py --help

# Run in different environments
APP_ENV=dev ./run.py
APP_ENV=test ./run.py
APP_ENV=prod ./run.py

# Check dependencies
pip list

# Update dependencies
pip install --upgrade -e .
```

## Production Deployment

### Using Docker (recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t card-verification .
docker run -p 8000:8000 --env-file .env card-verification
```

### Using Heroku

The `Procfile` is already configured:

```bash
heroku create your-app-name
heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
git push heroku main
```

## Support

For issues or questions:

1. Check the documentation in this repository
2. Review the FastAPI documentation: <https://fastapi.tiangolo.com>
3. Open an issue on GitHub

## License

MIT License
