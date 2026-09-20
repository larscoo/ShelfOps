import pytest

from app import create_app


@pytest.fixture(autouse=True)
def clear_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
