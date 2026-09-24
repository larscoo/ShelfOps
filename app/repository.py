"""Storage contract and process-local library collections."""

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Protocol

from app.models import Book, Copy, CopyWithStatus, Loan, Member


class RecordNotFoundError(LookupError):
    def __init__(self, entity: str):
        self.entity = entity
        super().__init__(f"{entity} not found.")


class CopyUnavailableError(Exception):
    """The copy already has an active loan."""


class StorageUnavailableError(Exception):
    """The configured storage cannot currently serve requests."""


class LibraryRepository(Protocol):
    persistent: bool

    def healthy(self) -> bool: ...

    def list_books(self) -> list[Book]: ...

    def add_book(self, title: str, author: str) -> Book: ...

    def list_members(self) -> list[Member]: ...

    def add_member(self, name: str) -> Member: ...

    def list_copies(self) -> list[CopyWithStatus]: ...

    def add_copy(self, book_id: int) -> CopyWithStatus: ...

    def list_loans(self) -> list[Loan]: ...

    def add_loan(self, copy_id: int, member_id: int) -> Loan: ...

    def return_loan(self, loan_id: int) -> Loan: ...


class InMemoryLibraryRepository:
    persistent = False

    def healthy(self) -> bool:
        return True

    def __init__(self, clock: Callable[[], datetime] | None = None):
        self._books: list[Book] = []
        self._members: list[Member] = []
        self._copies: list[Copy] = []
        self._loans: dict[int, Loan] = {}
        self._clock = clock if clock is not None else lambda: datetime.now(UTC)
        self._lock = Lock()

    def list_books(self) -> list[Book]:
        with self._lock:
            return list(self._books)

    def add_book(self, title: str, author: str) -> Book:
        with self._lock:
            book = Book(id=len(self._books) + 1, title=title, author=author)
            self._books.append(book)
            return book

    def list_members(self) -> list[Member]:
        with self._lock:
            return list(self._members)

    def add_member(self, name: str) -> Member:
        with self._lock:
            member = Member(id=len(self._members) + 1, name=name)
            self._members.append(member)
            return member

    def list_copies(self) -> list[CopyWithStatus]:
        with self._lock:
            now = self._clock()
            active = {
                loan.copy_id: loan for loan in self._loans.values() if loan.returned_at is None
            }
            copies = []
            for copy in self._copies:
                loan = active.get(copy.id)
                status = "available"
                if loan is not None:
                    status = "overdue" if now > loan.due_at else "on_loan"
                copies.append(CopyWithStatus(copy.id, copy.book_id, status))
            return copies

    def add_copy(self, book_id: int) -> CopyWithStatus:
        with self._lock:
            if not any(book.id == book_id for book in self._books):
                raise RecordNotFoundError("Book")
            copy = Copy(id=len(self._copies) + 1, book_id=book_id)
            self._copies.append(copy)
            return CopyWithStatus(copy.id, copy.book_id, "available")

    def list_loans(self) -> list[Loan]:
        with self._lock:
            return list(self._loans.values())

    def add_loan(self, copy_id: int, member_id: int) -> Loan:
        with self._lock:
            if not any(copy.id == copy_id for copy in self._copies):
                raise RecordNotFoundError("Copy")
            if not any(member.id == member_id for member in self._members):
                raise RecordNotFoundError("Member")
            if any(
                loan.copy_id == copy_id and loan.returned_at is None
                for loan in self._loans.values()
            ):
                raise CopyUnavailableError("Copy already has an active loan.")
            now = self._clock()
            loan = Loan(len(self._loans) + 1, copy_id, member_id, now, now + timedelta(days=28))
            self._loans[loan.id] = loan
            return loan

    def return_loan(self, loan_id: int) -> Loan:
        with self._lock:
            loan = self._loans.get(loan_id)
            if loan is None:
                raise RecordNotFoundError("Loan")
            if loan.returned_at is None:
                loan = replace(loan, returned_at=self._clock())
                self._loans[loan_id] = loan
            return loan
