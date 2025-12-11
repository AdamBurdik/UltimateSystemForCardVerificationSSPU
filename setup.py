#!/usr/bin/env python

from setuptools import setup, find_packages

dependencies = [
    # Flask and extensions
    "flask>=3.0.0",
    "flask-assets>=2.1.0",
    "flask-bcrypt>=1.0.0",
    "flask-login>=0.6.3",
    "flask-mail>=0.9.1",
    "flask-migrate>=4.0.0",
    "flask-wtf>=1.2.0",
    "Werkzeug>=3.0.0",
    # Asset minification
    "cssmin>=0.2.0",
    "libsass>=0.23.0",
    # Database
    "alembic>=1.13.0",
    "sqlalchemy>=2.0.0",
    "pymysql>=1.1.0",
    # Testing
    "pytest>=7.4.0",
    "webtest>=3.0.0",
    # Lint
    "pycodestyle>=2.11.0",
    "pylint>=3.0.0",
    # Production webserver
    "gunicorn>=21.2.0",
    # Utilities
    "simplejson>=3.19.0",
    "xmltodict>=0.13.0",
    "WTForms>=3.1.0",
    "WTForms-Components>=0.10.5",
    # MQTT and WebSocket
    "paho-mqtt>=1.6.0",
    "python-socketio>=5.10.0",
    "flask-socketio>=5.3.0",
]

setup(
    name="ultimate-card-verification-system",
    version="2.0.0",
    url="https://github.com/AdamBurdik/UltimateSystemForCardVerificationSSPU",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=dependencies
)
