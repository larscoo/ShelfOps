import os
import uuid

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import make_conninfo

from app import create_app
from app.postgres import PostgresLibraryRepository
from app.repository import InMemoryLibraryRepository


@pytest.fixture(autouse=True)
def clear_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)


@pytest.fixture(params=["memory", "postgres"])
def repository_factory(request):
    if request.param == "memory":
        yield InMemoryLibraryRepository
        return
    dsn = os.environ.get("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("PostgreSQL tests require TEST_DATABASE_URL; use make cov")
    schemas = []
    with psycopg.connect(dsn, autocommit=True) as admin:
        if admin.execute("SELECT current_database()").fetchone()[0] != "shelfops_test":
            pytest.fail("Integration tests require a dedicated database named shelfops_test")

        def factory(clock=None):
            schema = "test_" + uuid.uuid4().hex
            admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
            schemas.append(schema)
            return PostgresLibraryRepository(
                make_conninfo(dsn, options=f"-csearch_path={schema}"), clock=clock
            )

        try:
            yield factory
        finally:
            for schema in schemas:
                admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


@pytest.fixture
def client(repository_factory):
    app = create_app(repository=repository_factory())
    app.config["TESTING"] = True
    return app.test_client()
