"""Entry point for the local Flask server and later a WSGI server."""

from app import create_app

app = create_app()
