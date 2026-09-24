"""HTTP routes for books, members and physical copies."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from app.models import (
    Loan,
    ValidationError,
    validate_book,
    validate_copy,
    validate_loan,
    validate_member,
)
from app.repository import (
    CopyUnavailableError,
    LibraryRepository,
    RecordNotFoundError,
    StorageUnavailableError,
)

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


@bp.errorhandler(RecordNotFoundError)
def record_not_found(error):
    return jsonify(error=f"{error.entity.lower()}_not_found", message=str(error)), 404


@bp.errorhandler(CopyUnavailableError)
def copy_unavailable(error):
    return jsonify(error="copy_unavailable", message=str(error)), 409


@bp.errorhandler(StorageUnavailableError)
def storage_unavailable(error):
    return jsonify(error="storage_unavailable", message="Storage temporarily unavailable."), 503


def loan_json(loan: Loan) -> dict:
    data = asdict(loan)
    for field in ("loaned_at", "due_at", "returned_at"):
        data[field] = data[field].isoformat() if data[field] is not None else None
    return data


@bp.get("/")
def index():
    books = _repo().list_books()
    members = _repo().list_members()
    copies = _repo().list_copies()
    return render_template(
        "index.html",
        books=books,
        persistent=_repo().persistent,
        books_by_id={book.id: book for book in books},
        members=members,
        members_by_id={member.id: member for member in members},
        copies=copies,
        copies_by_id={copy.id: copy for copy in copies},
        available_copies=[copy for copy in copies if copy.status == "available"],
        loans=_repo().list_loans(),
        status_labels={"available": "Verfügbar", "on_loan": "Ausgeliehen", "overdue": "Überfällig"},
    )


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/ready")
def ready():
    if _repo().healthy():
        return jsonify(status="ready")
    return jsonify(status="not_ready"), 503


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
    return jsonify([asdict(copy) for copy in _repo().list_copies()])


@bp.post("/copies")
def create_copy():
    book_id = validate_copy(request.get_json())
    return jsonify(asdict(_repo().add_copy(book_id))), 201


@bp.get("/copies/stats")
def copy_stats():
    copies = _repo().list_copies()
    counts = {"available": 0, "on_loan": 0, "overdue": 0}
    for copy in copies:
        counts[copy.status] += 1
    return jsonify(total=len(copies), **counts)


@bp.get("/loans")
def list_loans():
    return jsonify([loan_json(loan) for loan in _repo().list_loans()])


@bp.post("/loans")
def create_loan():
    copy_id, member_id = validate_loan(request.get_json())
    return jsonify(loan_json(_repo().add_loan(copy_id, member_id))), 201


@bp.post("/loans/<int:loan_id>/return")
def return_loan(loan_id):
    if request.get_data():
        raise ValidationError("Return requests must have an empty body.")
    return jsonify(loan_json(_repo().return_loan(loan_id)))
