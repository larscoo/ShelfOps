import pytest

from app import create_app


def test_health_without_storage_access():
    class UnavailableRepository:
        def list_books(self):
            raise AssertionError("Health must not query storage")

        def add_book(self, title, author):
            raise AssertionError("Health must not modify storage")

    client = create_app(repository=UnavailableRepository()).test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_database_configuration_does_not_silently_use_memory(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/example")
    with pytest.raises(RuntimeError, match="PostgreSQL is not implemented"):
        create_app()
