"""PostgreSQL storage, following the CDS212 repository pattern.

Connections are short-lived transactions. Schema creation is lazy so /health
remains available even when the configured database is offline at startup.
"""

from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from threading import Lock

import psycopg

from app.models import Book, CopyWithStatus, Loan, Member
from app.repository import CopyUnavailableError, RecordNotFoundError, StorageUnavailableError

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(btrim(title)) BETWEEN 1 AND 200),
    author TEXT NOT NULL CHECK (length(btrim(author)) BETWEEN 1 AND 200)
);
CREATE TABLE IF NOT EXISTS members (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(btrim(name)) BETWEEN 1 AND 200)
);
CREATE TABLE IF NOT EXISTS copies (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL REFERENCES books(id)
);
CREATE TABLE IF NOT EXISTS loans (
    id BIGSERIAL PRIMARY KEY,
    copy_id BIGINT NOT NULL REFERENCES copies(id),
    member_id BIGINT NOT NULL REFERENCES members(id),
    loaned_at TIMESTAMPTZ NOT NULL,
    due_at TIMESTAMPTZ NOT NULL CHECK (due_at > loaned_at),
    returned_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_loan_per_copy
    ON loans(copy_id) WHERE returned_at IS NULL;
"""
LOAN_COLUMNS = "id, copy_id, member_id, loaned_at, due_at, returned_at"


class PostgresLibraryRepository:
    persistent = True

    def __init__(self, dsn: str, clock: Callable[[], datetime] | None = None):
        self._dsn = dsn
        self._clock = clock if clock is not None else lambda: datetime.now(UTC)
        self._initialized = False
        self._schema_lock = Lock()

    @contextmanager
    def _connection(self):
        try:
            with psycopg.connect(self._dsn, connect_timeout=3) as conn:
                conn.execute("SET TIME ZONE 'UTC'")
                conn.execute("SET statement_timeout = '5s'")
                if not self._initialized:
                    with self._schema_lock:
                        if not self._initialized:
                            # Serialize first-time DDL across Gunicorn workers.
                            conn.execute("SELECT pg_advisory_xact_lock(2122026)")
                            conn.execute(SCHEMA)
                            conn.commit()
                            self._initialized = True
                yield conn
        except (psycopg.OperationalError, psycopg.InterfaceError) as error:
            raise StorageUnavailableError("Database unavailable.") from error

    def healthy(self) -> bool:
        try:
            with self._connection() as conn:
                conn.execute("SELECT 1 FROM books LIMIT 1")
            return True
        except (StorageUnavailableError, psycopg.Error):
            return False

    def list_books(self) -> list[Book]:
        with self._connection() as conn:
            rows = conn.execute("SELECT id, title, author FROM books ORDER BY id").fetchall()
        return [Book(*row) for row in rows]

    def add_book(self, title: str, author: str) -> Book:
        with self._connection() as conn:
            row = conn.execute(
                "INSERT INTO books(title, author) VALUES (%s, %s) RETURNING id, title, author",
                (title, author),
            ).fetchone()
        return Book(*row)

    def list_members(self) -> list[Member]:
        with self._connection() as conn:
            rows = conn.execute("SELECT id, name FROM members ORDER BY id").fetchall()
        return [Member(*row) for row in rows]

    def add_member(self, name: str) -> Member:
        with self._connection() as conn:
            row = conn.execute(
                "INSERT INTO members(name) VALUES (%s) RETURNING id, name", (name,)
            ).fetchone()
        return Member(*row)

    def list_copies(self) -> list[CopyWithStatus]:
        with self._connection() as conn:
            rows = conn.execute(
                """SELECT c.id, c.book_id,
                   CASE WHEN l.id IS NULL THEN 'available'
                        WHEN %s > l.due_at THEN 'overdue' ELSE 'on_loan' END
                   FROM copies c LEFT JOIN loans l
                     ON l.copy_id = c.id AND l.returned_at IS NULL
                   ORDER BY c.id""",
                (self._clock(),),
            ).fetchall()
        return [CopyWithStatus(*row) for row in rows]

    def add_copy(self, book_id: int) -> CopyWithStatus:
        with self._connection() as conn:
            if conn.execute("SELECT id FROM books WHERE id = %s", (book_id,)).fetchone() is None:
                raise RecordNotFoundError("Book")
            row = conn.execute(
                "INSERT INTO copies(book_id) VALUES (%s) RETURNING id, book_id", (book_id,)
            ).fetchone()
        return CopyWithStatus(*row, "available")

    def list_loans(self) -> list[Loan]:
        with self._connection() as conn:
            rows = conn.execute(f"SELECT {LOAN_COLUMNS} FROM loans ORDER BY id").fetchall()
        return [Loan(*row) for row in rows]

    def add_loan(self, copy_id: int, member_id: int) -> Loan:
        try:
            with self._connection() as conn:
                if (
                    conn.execute(
                        "SELECT id FROM copies WHERE id = %s FOR UPDATE", (copy_id,)
                    ).fetchone()
                    is None
                ):
                    raise RecordNotFoundError("Copy")
                if (
                    conn.execute("SELECT id FROM members WHERE id = %s", (member_id,)).fetchone()
                    is None
                ):
                    raise RecordNotFoundError("Member")
                if (
                    conn.execute(
                        "SELECT id FROM loans WHERE copy_id = %s AND returned_at IS NULL",
                        (copy_id,),
                    ).fetchone()
                    is not None
                ):
                    raise CopyUnavailableError("Copy already has an active loan.")
                now = self._clock()
                row = conn.execute(
                    "INSERT INTO loans(copy_id, member_id, loaned_at, due_at) "
                    f"VALUES (%s, %s, %s, %s) RETURNING {LOAN_COLUMNS}",
                    (copy_id, member_id, now, now + timedelta(days=28)),
                ).fetchone()
            return Loan(*row)
        except psycopg.errors.UniqueViolation as error:
            if error.diag.constraint_name != "one_active_loan_per_copy":
                raise
            raise CopyUnavailableError("Copy already has an active loan.") from error

    def return_loan(self, loan_id: int) -> Loan:
        with self._connection() as conn:
            row = conn.execute(
                f"SELECT {LOAN_COLUMNS} FROM loans WHERE id = %s FOR UPDATE", (loan_id,)
            ).fetchone()
            if row is None:
                raise RecordNotFoundError("Loan")
            if row[5] is None:
                row = conn.execute(
                    f"UPDATE loans SET returned_at = %s WHERE id = %s RETURNING {LOAN_COLUMNS}",
                    (self._clock(), loan_id),
                ).fetchone()
        return Loan(*row)
