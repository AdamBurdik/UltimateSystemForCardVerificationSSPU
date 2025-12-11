#!/usr/bin/env python

from setuptools import setup, find_packages

dependencies = [
    # FastAPI and core
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "python-multipart>=0.0.12",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    # Database
    "alembic>=1.13.0",
    "sqlalchemy>=2.0.0",
    "pymysql>=1.1.0",
    # Authentication
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    # Email
    "fastapi-mail>=1.4.0",
    # Templates
    "jinja2>=3.1.0",
    # Testing
    "pytest>=7.4.0",
    "httpx>=0.27.0",
    "pytest-asyncio>=0.24.0",
    # Utilities
    "simplejson>=3.19.0",
    "xmltodict>=0.13.0",
    # MQTT and WebSocket
    "paho-mqtt>=1.6.0",
    "websockets>=13.0",
    # Production server
    "gunicorn>=21.2.0",
]

setup(
    name="ultimate-card-verification-system",
    version="3.0.0",
    url="https://github.com/AdamBurdik/UltimateSystemForCardVerificationSSPU",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=dependencies
)
