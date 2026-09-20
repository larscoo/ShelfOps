"""HTTP routes for the first ShelfOps increment."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from app.models import validate_book
from app.repository import BookRepository

bp = Blueprint("api", __name__)


def _repo() -> BookRepository:
    return current_app.extensions["book_repository"]


@bp.get("/")
def index():
    return render_template("index.html", books=_repo().list_books())


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/books")
def list_books():
    return jsonify([asdict(book) for book in _repo().list_books()])


@bp.post("/books")
def create_book():
    try:
        payload = request.get_json()
    except UnsupportedMediaType:
        return jsonify(error="unsupported_media_type", message="Use application/json."), 415
    except BadRequest:
        return jsonify(error="invalid_json", message="Request body must be valid JSON."), 400

    try:
        title, author = validate_book(payload)
    except ValueError as error:
        return jsonify(error="invalid_input", message=str(error)), 400

    return jsonify(asdict(_repo().add_book(title, author))), 201
