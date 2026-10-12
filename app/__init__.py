"""Application factory: each instance owns its own storage."""

import os

from flask import Flask
from prometheus_client import CollectorRegistry
from prometheus_flask_exporter import PrometheusMetrics

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
    app.config["APP_VERSION"] = os.environ.get("APP_VERSION", "0.1.0")
    app.config["APP_COMMIT"] = os.environ.get("RENDER_GIT_COMMIT", "unknown")
    app.extensions["library_repository"] = repository
    app.register_blueprint(bp)
    metrics = PrometheusMetrics(app, registry=CollectorRegistry())
    metrics.info(
        "shelfops_info",
        "Application info",
        version=app.config["APP_VERSION"],
    )
    return app
