"""Book data and validation independent of HTTP and storage."""

from dataclasses import dataclass

MAX_TEXT_LENGTH = 200


def validate_book(payload: object) -> tuple[str, str]:
    if not isinstance(payload, dict) or set(payload) != {"title", "author"}:
        raise ValueError("Exactly title and author are required.")

    values = []
    for field in ("title", "author"):
        value = payload[field]
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= MAX_TEXT_LENGTH:
            raise ValueError(f"{field} must contain 1 to {MAX_TEXT_LENGTH} characters.")
        values.append(value.strip())
    return values[0], values[1]


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str
