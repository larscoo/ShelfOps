"""Storage contract and a process-local book collection."""

from threading import Lock
from typing import Protocol

from app.models import Book


class BookRepository(Protocol):
    def list_books(self) -> list[Book]: ...

    def add_book(self, title: str, author: str) -> Book: ...


class InMemoryBookRepository:
    def __init__(self):
        self._books: list[Book] = []
        self._lock = Lock()

    def list_books(self) -> list[Book]:
        with self._lock:
            return list(self._books)

    def add_book(self, title: str, author: str) -> Book:
        with self._lock:
            book = Book(id=len(self._books) + 1, title=title, author=author)
            self._books.append(book)
            return book
