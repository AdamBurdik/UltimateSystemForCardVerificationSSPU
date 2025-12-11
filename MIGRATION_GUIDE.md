# Migration Guide: Upgrading to v2.0

This guide helps you upgrade from the old Flask Skeleton-based version to the modern v2.0 with Flask 3.x and Python 3.8+.

## Prerequisites

Before starting the migration, ensure you have:
- Python 3.8 or higher installed
- A backup of your database
- All current data exported if needed

## Step-by-Step Migration

### 1. Backup Your Data

```bash
# Backup your database
mysqldump -u username -p dbname > backup_$(date +%Y%m%d).sql

# Or for SQLite
cp dev.db dev.db.backup
```

### 2. Update Python Environment

```bash
# Remove old virtual environment
rm -rf venv/
# or if using the Makefile version:
rm -rf ~/.virtualenvs/flask-skeleton/

# Create new virtual environment with Python 3
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install New Dependencies

```bash
# Install the updated package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### 4. Update Environment Variables

The `.env` file format remains the same, but verify you have all required variables:

```bash
# Required
APP_KEY=your-secret-key-here

# Email configuration (if using email features)
APP_MAIL_USERNAME=your-email@gmail.com
APP_MAIL_PASSWORD=your-app-password
APP_MAIL_INFO_ACCOUNT=info@example.com
APP_TEST_RECIPIENT=test@example.com

# Database (production)
DATABASE_URL=mysql+pymysql://user:password@host/database?charset=utf8
```

**Note:** The mail server now correctly uses port 587 with TLS instead of the incorrect port 564.

### 5. Update Management Commands

The old `flask-script` based commands have been replaced with Flask CLI:

#### Old Command → New Command

```bash
# Running the server
./manage.py runserver              → ./manage.py runserver
# or use Flask CLI:
                                   → flask run

# Database migrations
./manage.py db upgrade             → flask db upgrade
./manage.py db migrate             → flask db migrate
./manage.py db history             → flask db history

# Shell
./manage.py shell                  → ./manage.py shell
# or:
                                   → flask shell

# Routes
./manage.py routes                 → ./manage.py routes

# Test email
./manage.py test email             → ./manage.py test_email
```

### 6. Database Migrations

The database schema hasn't changed, but you should verify migrations work:

```bash
# Check current migration state
flask db current

# Apply any pending migrations
flask db upgrade
```

### 7. Code Changes (If You've Customized)

If you've made custom modifications to the codebase, you may need to update:

#### Python 2 → Python 3
- `print statement` → `print(function)`
- `dict.iteritems()` → `dict.items()`
- `dict.itervalues()` → `dict.values()`
- `raw_input()` → `input()`

#### Flask Changes
- `from flask import escape` → `from markupsafe import escape`
- `from flask_wtf import Form` → `from flask_wtf import FlaskForm`

#### WTForms Changes
- `TextField` → `StringField`
- `@pytest.yield_fixture` → `@pytest.fixture`

#### SQLAlchemy 2.0 Changes
- `URL(drivername='sqlite', database=path)` → `f'sqlite:///{path}'`
- Removed deprecated `Query` patterns (use `select()` for new code)

### 8. Testing

Run the test suite to verify everything works:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest test/test_config.py
```

### 9. Production Deployment

When deploying to production:

```bash
# Set environment
export APP_ENV=prod

# Install production dependencies
pip install -e .

# Run database migrations
flask db upgrade

# Start with gunicorn (example)
gunicorn -w 4 -b 0.0.0.0:8000 'src.app:create_app(src.settings.app_config)'
```

## Known Issues

### Database Queries at Import Time

Some forms execute database queries during class definition (e.g., `MonthInsert` form). This is a design issue that may cause import errors if the database isn't available. 

**Workaround:** Ensure the database is accessible before importing the application, or refactor forms to use dynamic choices.

### Asset Compilation

The SCSS compiler has been changed from `pyscss` to `libsass`. If you have custom SCSS:

1. Verify your SCSS files are compatible with libsass
2. Delete old compiled assets: `rm -rf src/static/css/*.min.css`
3. Let Flask-Assets rebuild on first run

## Rollback Procedure

If you need to rollback:

```bash
# Restore database backup
mysql -u username -p dbname < backup_YYYYMMDD.sql

# Restore old environment
git checkout <old-version-tag>
pip install -r old-requirements.txt
```

## Benefits of v2.0

- **Security:** No known vulnerabilities in dependencies
- **Performance:** Modern Flask 3.x with better performance
- **Compatibility:** Works with Python 3.8-3.12
- **Maintainability:** Up-to-date dependencies with active support
- **Features:** Access to modern Flask and SQLAlchemy features

## Support

For issues or questions:
1. Check the updated [README.md](README.md)
2. Review error messages and logs
3. Open an issue on GitHub

## Version Compatibility Matrix

| Component | Old Version | New Version |
|-----------|-------------|-------------|
| Python | 2.7 | 3.8+ |
| Flask | 0.10.1 | 3.1.2+ |
| SQLAlchemy | 0.9.3 | 2.0.45+ |
| WTForms | 0.9.5 | 3.2.1+ |
| Alembic | 0.6.5 | 1.17.2+ |
| pytest | 2.5.2 | 7.4.0+ |

All dependencies have been updated to their latest stable versions as of 2024.
