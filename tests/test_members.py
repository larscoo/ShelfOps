import pytest

from app import create_app


def test_members_are_empty_initially(client):
    response = client.get("/members")
    assert response.status_code == 200
    assert response.json == []


def test_create_trimmed_members_with_duplicate_names(client):
    first = client.post("/members", json={"name": "  Alex Beispiel  "})
    second = client.post("/members", json={"name": "Alex Beispiel"})
    assert first.status_code == second.status_code == 201
    assert first.json == {"id": 1, "name": "Alex Beispiel"}
    assert second.json == {"id": 2, "name": "Alex Beispiel"}
    assert client.get("/members").json == [first.json, second.json]
    assert create_app().test_client().get("/members").json == []


@pytest.mark.parametrize("value", ["", " \t ", "a" * 201, None, True, 5, [], {}])
def test_invalid_names_do_not_create_members(client, value):
    response = client.post("/members", json={"name": value})
    assert response.status_code == 400
    assert response.json["error"] == "invalid_input"
    assert client.get("/members").json == []


def test_maximum_member_name_length(client):
    response = client.post("/members", json={"name": "a" * 200})
    assert response.status_code == 201
    assert response.json["name"] == "a" * 200


@pytest.mark.parametrize("payload", [{}, [], "Alex", {"name": "Alex", "id": 5}])
def test_reject_member_shape(client, payload):
    response = client.post("/members", json=payload)
    assert response.status_code == 400
    assert client.get("/members").json == []
