"""Library data and validation independent of HTTP and storage."""

from dataclasses import dataclass
from datetime import datetime

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
    return validate_id(data["book_id"], "book_id")


def validate_id(value: object, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValidationError(f"{field} must be a positive integer.")
    return value


def validate_loan(payload: object) -> tuple[int, int]:
    data = require_fields(payload, {"copy_id", "member_id"})
    return validate_id(data["copy_id"], "copy_id"), validate_id(data["member_id"], "member_id")


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


@dataclass(frozen=True)
class CopyWithStatus(Copy):
    """Read-only snapshot; status is derived from active loans."""

    status: str


@dataclass(frozen=True)
class Loan:
    id: int
    copy_id: int
    member_id: int
    loaned_at: datetime
    due_at: datetime
    returned_at: datetime | None = None
