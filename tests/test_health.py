from app import create_app
from app.postgres import PostgresLibraryRepository


def test_health_without_storage_access():
    class UnavailableRepository:
        def list_books(self):
            raise AssertionError("Health must not query storage")

        def add_book(self, title, author):
            raise AssertionError("Health must not modify storage")

    client = create_app(repository=UnavailableRepository()).test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "version": "0.1.0", "commit": "unknown"}


def test_health_reports_deployed_version_without_database(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.0.0")
    monkeypatch.setenv("RENDER_GIT_COMMIT", "a" * 40)
    monkeypatch.setenv("DATABASE_URL", "postgresql://127.0.0.1:1/unavailable")
    response = create_app().test_client().get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "version": "1.0.0", "commit": "a" * 40}


def test_database_configuration_does_not_silently_use_memory(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://127.0.0.1:1/unavailable")
    app = create_app()
    assert isinstance(app.extensions["library_repository"], PostgresLibraryRepository)
    client = app.test_client()
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 503
    response = client.get("/books")
    assert response.status_code == 503
    assert response.json["error"] == "storage_unavailable"
    assert "postgresql" not in response.text


def test_readiness_of_available_storage(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json == {"status": "ready"}
