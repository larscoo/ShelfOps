import pytest

from app import create_app


def test_empty_catalog(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json == []


def test_create_and_list_books(client):
    first = client.post("/books", json={"title": "  The Trial  ", "author": " Franz Kafka "})
    assert first.status_code == 201
    assert first.json == {"id": 1, "title": "The Trial", "author": "Franz Kafka"}
    second = client.post("/books", json={"title": "The Trial", "author": "Franz Kafka"})
    assert second.status_code == 201
    assert second.json["id"] == 2
    assert client.get("/books").json == [first.json, second.json]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "Book"},
        {"author": "Author"},
        {"title": "Book", "author": "Author", "id": 7},
        [],
        "book",
        42,
    ],
)
def test_reject_invalid_shape_without_mutation(client, payload):
    response = client.post("/books", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "invalid_input"
    assert client.get("/books").json == []


@pytest.mark.parametrize("field", ["title", "author"])
@pytest.mark.parametrize("value", ["", " \t ", "x" * 201, None, 12, True, [], {}])
def test_reject_invalid_text(client, field, value):
    payload = {"title": "Book", "author": "Author", field: value}
    response = client.post("/books", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "invalid_input"
    assert "message" in response.json
    assert client.get("/books").json == []


def test_accept_maximum_text_lengths(client):
    response = client.post("/books", json={"title": "a" * 200, "author": "b" * 200})
    assert response.status_code == 201


@pytest.mark.parametrize("body", ["{", "", "null"])
def test_reject_invalid_json_or_null(client, body):
    response = client.post("/books", data=body, content_type="application/json")
    assert response.status_code == 400
    assert client.get("/books").json == []


def test_reject_non_json_content_type(client):
    response = client.post("/books", data="title=Book&author=Author")
    assert response.status_code == 415
    assert response.json["error"] == "unsupported_media_type"
    assert client.get("/books").json == []


def test_instances_do_not_share_books(client):
    client.post("/books", json={"title": "Book", "author": "Author"})
    assert create_app().test_client().get("/books").json == []
