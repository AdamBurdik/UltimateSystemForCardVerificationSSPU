import os
import logging


class Config:
    # controls whether web interface users are in Flask debug mode
    # (e.g. Werkzeug stack trace console, unminified assets)
    DEBUG = False

    # Encryption key used to sign Flask session cookies
    # Generate a random one using os.urandom(24)
    SECRET_KEY = os.environ.get('APP_KEY')

    # Logging
    APP_LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_LOG_LEVEL = logging.WARN
    STDERR_LOG_FORMAT = ('%(asctime)s %(levelname)s %(message)s', '%m/%d/%Y %I:%M:%S %p')

    # Useful directories
    APP_DIR = os.path.dirname(os.path.abspath(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    STATIC_DIR = os.path.join(APP_DIR, 'static')

    # Number of rounds for bcrypt hashing
    # timeit Bcrypt().generate_password_hash('some12uihr3', 3) ~ 1.49ms per loop
    BCRYPT_LOG_ROUNDS = 4

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # The account used to authenticate gmail service
    MAIL_USERNAME = os.environ.get('APP_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('APP_MAIL_PASSWORD')

    # Mail accounts
    INFO_ACCOUNT = os.environ.get('APP_MAIL_INFO_ACCOUNT')
    TEST_RECIPIENT = os.environ.get('APP_TEST_RECIPIENT')
    MAIL_DEFAULT_SENDER = INFO_ACCOUNT


class DevelopmentConfig(Config):
    ENV = 'dev'
    DEBUG = True

    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'


class TestConfig(Config):
    ENV = 'test'
    TESTING = True

    # Dummy secret key for running tests
    SECRET_KEY = 'test'

    # Don't want to see info messages about managing posts
    APP_LOG_LEVEL = logging.WARN

    # Use in-memory test database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # For faster testing
    BCRYPT_LOG_ROUNDS = 1

    # Allows form testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    ENV = 'prod'

    # Don't need to see debug messages in production
    APP_LOG_LEVEL = logging.INFO

    # This must be defined in environment or Heroku
    # Default to a fallback MySQL connection if not set
    default_db_url = 'mysql+pymysql://root:root@192.168.1.110/karty?charset=utf8'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default_db_url)

    # Increase rounds for production instances
    # timeit Bcrypt().generate_password_hash('some12uihr3', 7) ~ 11.4ms per loop
    BCRYPT_LOG_ROUNDS = 7


config_dict = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}

app_config = config_dict[os.getenv('APP_ENV') or 'default']
