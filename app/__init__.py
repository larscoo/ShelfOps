"""Application factory: each instance owns its own storage."""

import os

from flask import Flask

from app.repository import InMemoryLibraryRepository, LibraryRepository
from app.routes import bp


def create_app(repository: LibraryRepository | None = None) -> Flask:
    if os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "PostgreSQL is not implemented yet. Unset DATABASE_URL for this version."
        )
    app = Flask(__name__)
    app.extensions["library_repository"] = (
        repository if repository is not None else InMemoryLibraryRepository()
    )
    app.register_blueprint(bp)
    return app
