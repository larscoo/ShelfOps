"""Application factory: each instance owns its own storage."""

import os

from flask import Flask

from app.repository import BookRepository, InMemoryBookRepository
from app.routes import bp


def create_app(repository: BookRepository | None = None) -> Flask:
    if os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "PostgreSQL is not implemented yet. Unset DATABASE_URL for this version."
        )
    app = Flask(__name__)
    app.extensions["book_repository"] = (
        repository if repository is not None else InMemoryBookRepository()
    )
    app.register_blueprint(bp)
    return app
