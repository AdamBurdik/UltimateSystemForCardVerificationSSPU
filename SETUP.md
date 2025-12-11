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

Create a `.env` file in the project root directory:
**Ensure that it is encoded in plain UTF-8!!!**

```bash
# Generate a secure secret key
py -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" > .env

# Add database URL (SQLite for development)
echo "DATABASE_URL=sqlite:///./dev.db" >> .env
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
# Using the run.py script
./run.py --reload

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

### Using curl

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

### Import Errors

If you get import errors, make sure you're in the project root and the virtual environment is activated:

```bash
pwd  # Should show the project directory
which python  # Should show the venv python
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
./run.py --port 8080

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9  # Linux/macOS
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
