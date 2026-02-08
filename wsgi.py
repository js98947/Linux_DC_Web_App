"""WSGI entry point for production deployment."""

import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app

application = create_app(os.environ.get("FLASK_ENV", "production"))
