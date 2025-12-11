#!/usr/bin/env python

"""
Manage script for development using Flask CLI
"""
import os
import click
from flask.cli import FlaskGroup

from src.app import create_app
from src.settings import app_config
from src.data.base import Base
from src.data.database import db
from src.data import models


def load_env():
    """Load environment variables from .env file"""
    if os.path.exists('.env'):
        print('Importing environment from .env...')
        for line in open('.env'):
            var = line.strip().split('=', 1)
            if len(var) == 2:
                os.environ[var[0]] = var[1]


load_env()


def create_app_wrapper(info=None):
    """Create app with config"""
    app = create_app(app_config)
    app.secret_key = os.environ.get('APP_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['ALLOWED_EXTENSIONS'] = {'xml'}
    if 'DATABASE_URL' in os.environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    return app


@click.group(cls=FlaskGroup, create_app=create_app_wrapper)
def cli():
    """Management script for the application."""
    pass


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug/--no-debug', default=True, help='Enable debug mode')
def runserver(host, port, debug):
    """Run the development server."""
    app = create_app_wrapper()
    app.run(host=host, port=port, debug=debug)


@cli.command()
def shell():
    """
    Starts a python shell with app, db and models loaded
    """
    import code
    app = create_app_wrapper()
    with app.app_context():
        # Loads all the models which inherit from Base
        models_map = {name: cls for name, cls in models.__dict__.items() 
                     if isinstance(cls, type) and hasattr(cls, '__bases__') 
                     and Base in cls.__mro__}
        context = dict(app=app, db=db, **models_map)
        code.interact(local=context)


@cli.command()
def test_email():
    """
    Send a test email -- useful for ensuring flask-mail is set up correctly
    """
    from flask_mail import Mail, Message
    app = create_app_wrapper()
    with app.app_context():
        mail = Mail(app)
        msg = Message(
            subject='test subject',
            recipients=[app.config.get('TEST_RECIPIENT', 'test@example.com')]
        )
        msg.body = 'text body'
        msg.html = '<b>HTML</b> body'
        mail.send(msg)
        print('Test email sent!')


@cli.command()
def routes():
    """Show all registered routes"""
    app = create_app_wrapper()
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f'{rule.endpoint:50s} {methods:20s} {rule.rule}')


if __name__ == '__main__':
    cli()