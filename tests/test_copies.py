from concurrent.futures import ThreadPoolExecutor

import pytest

from app import create_app


def test_copies_are_empty_initially(client):
    response = client.get("/copies")
    assert response.status_code == 200
    assert response.json == []


def test_multiple_copies_reference_the_right_books(client):
    first_book = client.post("/books", json={"title": "First", "author": "A"}).json
    second_book = client.post("/books", json={"title": "Second", "author": "B"}).json
    copies = []
    for book in (first_book, first_book, second_book):
        response = client.post("/copies", json={"book_id": book["id"]})
        assert response.status_code == 201
        copies.append(response.json)
    assert copies == [
        {"id": 1, "book_id": 1, "status": "available"},
        {"id": 2, "book_id": 1, "status": "available"},
        {"id": 3, "book_id": 2, "status": "available"},
    ]
    assert client.get("/copies").json == copies
    assert client.get("/books").json == [first_book, second_book]
    assert create_app().test_client().get("/copies").json == []


def test_unknown_book_is_rejected_without_consuming_an_id(client):
    response = client.post("/copies", json={"book_id": 123})
    assert response.status_code == 404
    assert response.json == {"error": "book_not_found", "message": "Book not found."}
    assert client.get("/copies").json == []
    assert client.get("/books").json == []
    book = client.post("/books", json={"title": "Book", "author": "Author"}).json
    response = client.post("/copies", json={"book_id": book["id"]})
    assert response.status_code == 201
    assert response.json["id"] == 1


@pytest.mark.parametrize("value", [0, -1, 1.0, "1", True, False, None, [], {}])
def test_copy_requires_a_positive_integer_book_id(client, value):
    client.post("/books", json={"title": "Book", "author": "Author"})
    response = client.post("/copies", json={"book_id": value})
    assert response.status_code == 400
    assert response.json["error"] == "invalid_input"
    assert client.get("/copies").json == []


@pytest.mark.parametrize("payload", [{}, [], "1", {"book_id": 1, "status": "available"}])
def test_reject_copy_shape(client, payload):
    response = client.post("/copies", json=payload)
    assert response.status_code == 400
    assert client.get("/copies").json == []


@pytest.mark.parametrize("path", ["/copies", "/members"])
def test_new_routes_reject_non_json_and_malformed_json(client, path):
    assert client.post(path, data="name=Alex").status_code == 415
    for body in ("{", "", "null"):
        assert client.post(path, data=body, content_type="application/json").status_code == 400
    assert client.get(path).json == []


def test_concurrent_copy_creation_has_distinct_ids(repository_factory):
    app = create_app(repository=repository_factory())
    app.config["TESTING"] = True
    with app.test_client() as client:
        client.post("/books", json={"title": "Book", "author": "Author"})

    def add_copy(_):
        with app.test_client() as client:
            response = client.post("/copies", json={"book_id": 1})
            assert response.status_code == 201
            return response.json["id"]

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(add_copy, range(20)))
    assert sorted(ids) == list(range(1, 21))
    assert len(app.test_client().get("/copies").json) == 20
