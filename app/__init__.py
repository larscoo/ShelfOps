"""Application factory: each instance owns its own storage."""

import os

from flask import Flask

from app.postgres import PostgresLibraryRepository
from app.repository import InMemoryLibraryRepository, LibraryRepository
from app.routes import bp


def create_app(repository: LibraryRepository | None = None) -> Flask:
    database_url = os.environ.get("DATABASE_URL")
    if repository is None:
        repository = (
            PostgresLibraryRepository(database_url) if database_url else InMemoryLibraryRepository()
        )
    app = Flask(__name__)
    app.extensions["library_repository"] = repository
    app.register_blueprint(bp)
    return app
