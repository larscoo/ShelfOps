"""Storage contract and process-local library collections."""

from threading import Lock
from typing import Protocol

from app.models import Book, Copy, Member


class BookNotFoundError(LookupError):
    """An exemplar cannot reference a missing book."""


class LibraryRepository(Protocol):
    def list_books(self) -> list[Book]: ...

    def add_book(self, title: str, author: str) -> Book: ...

    def list_members(self) -> list[Member]: ...

    def add_member(self, name: str) -> Member: ...

    def list_copies(self) -> list[Copy]: ...

    def add_copy(self, book_id: int) -> Copy: ...


class InMemoryLibraryRepository:
    def __init__(self):
        self._books: list[Book] = []
        self._members: list[Member] = []
        self._copies: list[Copy] = []
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

    def list_copies(self) -> list[Copy]:
        with self._lock:
            return list(self._copies)

    def add_copy(self, book_id: int) -> Copy:
        with self._lock:
            if not any(book.id == book_id for book in self._books):
                raise BookNotFoundError("Book not found.")
            copy = Copy(id=len(self._copies) + 1, book_id=book_id)
            self._copies.append(copy)
            return copy
