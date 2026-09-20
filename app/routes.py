"""HTTP routes for books, members and physical copies."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from app.models import ValidationError, validate_book, validate_copy, validate_member
from app.repository import BookNotFoundError, LibraryRepository

bp = Blueprint("api", __name__)


def _repo() -> LibraryRepository:
    return current_app.extensions["library_repository"]


@bp.errorhandler(UnsupportedMediaType)
def unsupported_media_type(error):
    return jsonify(error="unsupported_media_type", message="Use application/json."), 415


@bp.errorhandler(BadRequest)
def invalid_json(error):
    return jsonify(error="invalid_json", message="Request body must be valid JSON."), 400


@bp.errorhandler(ValidationError)
def invalid_input(error):
    return jsonify(error="invalid_input", message=str(error)), 400


@bp.errorhandler(BookNotFoundError)
def book_not_found(error):
    return jsonify(error="book_not_found", message=str(error)), 404


@bp.get("/")
def index():
    books = _repo().list_books()
    return render_template(
        "index.html",
        books=books,
        books_by_id={book.id: book for book in books},
        members=_repo().list_members(),
        copies=_repo().list_copies(),
    )


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/books")
def list_books():
    return jsonify([asdict(book) for book in _repo().list_books()])


@bp.post("/books")
def create_book():
    title, author = validate_book(request.get_json())
    return jsonify(asdict(_repo().add_book(title, author))), 201


@bp.get("/members")
def list_members():
    return jsonify([asdict(member) for member in _repo().list_members()])


@bp.post("/members")
def create_member():
    name = validate_member(request.get_json())
    return jsonify(asdict(_repo().add_member(name))), 201


@bp.get("/copies")
def list_copies():
    # All copies are available until the loans increment adds derived states.
    return jsonify([asdict(copy) | {"status": "available"} for copy in _repo().list_copies()])


@bp.post("/copies")
def create_copy():
    book_id = validate_copy(request.get_json())
    return jsonify(asdict(_repo().add_copy(book_id)) | {"status": "available"}), 201
