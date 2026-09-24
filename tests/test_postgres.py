from datetime import UTC, datetime, timedelta

import psycopg
import pytest

from app import create_app
from app.postgres import PostgresLibraryRepository


@pytest.fixture
def postgres(repository_factory):
    repository = repository_factory()
    if not repository.persistent:
        pytest.skip("PostgreSQL-specific storage checks")
    return repository


def test_new_repository_instance_sees_existing_data(postgres):
    book = postgres.add_book("A title with 'quotes'", "Author")
    member = postgres.add_member("Alex Example")
    copy = postgres.add_copy(book.id)
    loan = postgres.add_loan(copy.id, member.id)
    other = PostgresLibraryRepository(postgres._dsn)
    assert other.list_books() == [book]
    assert other.list_members() == [member]
    assert other.list_loans() == [loan]
    assert other.list_copies()[0].status == "on_loan"
    assert other.healthy()
    page = create_app(repository=other).test_client().get("/")
    assert "Daten werden dauerhaft gespeichert" in page.text
    assert "Beim Neustart werden alle" not in page.text


def test_database_index_blocks_duplicate_even_without_application_checks(postgres):
    book = postgres.add_book("Book", "Author")
    member = postgres.add_member("Member")
    copy = postgres.add_copy(book.id)
    postgres.add_loan(copy.id, member.id)
    now = datetime.now(UTC)
    with pytest.raises(psycopg.errors.UniqueViolation):
        with psycopg.connect(postgres._dsn) as conn:
            conn.execute(
                "INSERT INTO loans(copy_id,member_id,loaned_at,due_at) VALUES (%s,%s,%s,%s)",
                (copy.id, member.id, now, now + timedelta(days=28)),
            )
    assert len(postgres.list_loans()) == 1


def test_database_foreign_keys_reject_orphan_copies(postgres):
    assert postgres.healthy()
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with psycopg.connect(postgres._dsn) as conn:
            conn.execute("INSERT INTO copies(book_id) VALUES (999)")
    assert postgres.list_copies() == []
