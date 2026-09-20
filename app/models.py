"""Library data and validation independent of HTTP and storage."""

from dataclasses import dataclass

MAX_TEXT_LENGTH = 200


class ValidationError(ValueError):
    """A request does not match the input contract."""


def require_fields(payload: object, fields: set[str]) -> dict:
    if not isinstance(payload, dict) or set(payload) != fields:
        raise ValidationError(f"Exactly {', '.join(sorted(fields))} are required.")
    return payload


def validate_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= MAX_TEXT_LENGTH:
        raise ValidationError(f"{field} must contain 1 to {MAX_TEXT_LENGTH} characters.")
    return value.strip()


def validate_book(payload: object) -> tuple[str, str]:
    data = require_fields(payload, {"title", "author"})
    return validate_text(data["title"], "title"), validate_text(data["author"], "author")


def validate_member(payload: object) -> str:
    data = require_fields(payload, {"name"})
    return validate_text(data["name"], "name")


def validate_copy(payload: object) -> int:
    data = require_fields(payload, {"book_id"})
    book_id = data["book_id"]
    if type(book_id) is not int or book_id <= 0:
        raise ValidationError("book_id must be a positive integer.")
    return book_id


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str


@dataclass(frozen=True)
class Member:
    id: int
    name: str


@dataclass(frozen=True)
class Copy:
    id: int
    book_id: int
