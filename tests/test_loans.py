from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app import create_app


@pytest.fixture
def library(repository_factory):
    clock = SimpleNamespace(now=datetime(2026, 9, 20, 12, 0, tzinfo=UTC))
    repo = repository_factory(clock=lambda: clock.now)
    app = create_app(repository=repo)
    app.config["TESTING"] = True
    client = app.test_client()
    client.post("/books", json={"title": "The Trial", "author": "Franz Kafka"})
    client.post("/copies", json={"book_id": 1})
    client.post("/copies", json={"book_id": 1})
    client.post("/members", json={"name": "Alex Example"})
    return SimpleNamespace(app=app, client=client, clock=clock)


def borrow(client, copy_id=1, member_id=1):
    return client.post("/loans", json={"copy_id": copy_id, "member_id": member_id})


def test_loan_dates_and_unlimited_member_loans(library):
    client = library.client
    assert client.get("/loans").json == []
    first = borrow(client)
    assert first.status_code == 201
    assert first.json == {
        "id": 1,
        "copy_id": 1,
        "member_id": 1,
        "loaned_at": "2026-09-20T12:00:00+00:00",
        "due_at": "2026-10-18T12:00:00+00:00",
        "returned_at": None,
    }
    assert [c["status"] for c in client.get("/copies").json] == ["on_loan", "available"]
    second = borrow(client, copy_id=2)
    assert second.status_code == 201
    assert client.get("/loans").json == [first.json, second.json]
    assert create_app().test_client().get("/loans").json == []


def test_due_boundary_and_overdue_copy_cannot_be_borrowed(library):
    client = library.client
    loan = borrow(client).json
    library.clock.now = datetime.fromisoformat(loan["due_at"])
    assert client.get("/copies").json[0]["status"] == "on_loan"
    library.clock.now += timedelta(microseconds=1)
    assert client.get("/copies").json[0]["status"] == "overdue"
    conflict = borrow(client)
    assert conflict.status_code == 409
    assert conflict.json["error"] == "copy_unavailable"
    assert client.get("/loans").json == [loan]


@pytest.mark.parametrize("days", [1, 29])
def test_return_then_reborrow_and_repeat_old_return(library, days):
    client = library.client
    original = borrow(client).json
    library.clock.now += timedelta(days=days)
    returned = client.post("/loans/1/return")
    assert returned.status_code == 200
    assert returned.json["returned_at"] == library.clock.now.isoformat()
    assert returned.json["loaned_at"] == original["loaned_at"]
    assert returned.json["due_at"] == original["due_at"]
    assert client.get("/copies").json[0]["status"] == "available"
    second = borrow(client)
    assert second.status_code == 201
    assert second.json["id"] == 2
    library.clock.now += timedelta(days=1)
    assert client.post("/loans/1/return").json == returned.json
    assert client.get("/copies").json[0]["status"] == "on_loan"
    assert client.get("/loans").json == [returned.json, second.json]


def test_active_loan_blocks_other_members(library):
    client = library.client
    client.post("/members", json={"name": "Second Member"})
    loan = borrow(client).json
    assert borrow(client, member_id=2).status_code == 409
    assert client.get("/loans").json == [loan]


@pytest.mark.parametrize(
    "copy_id, member_id, code", [(99, 1, "copy_not_found"), (1, 99, "member_not_found")]
)
def test_unknown_references_have_no_side_effects(library, copy_id, member_id, code):
    response = borrow(library.client, copy_id, member_id)
    assert response.status_code == 404
    assert response.json["error"] == code
    assert library.client.get("/loans").json == []
    assert borrow(library.client).json["id"] == 1


@pytest.mark.parametrize("field", ["copy_id", "member_id"])
@pytest.mark.parametrize("value", [0, -1, 1.0, "1", True, None, [], {}])
def test_loan_ids_must_be_positive_integers(library, field, value):
    payload = {"copy_id": 1, "member_id": 1, field: value}
    response = library.client.post("/loans", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "invalid_input"
    assert library.client.get("/loans").json == []


@pytest.mark.parametrize(
    "payload",
    [{}, [], {"copy_id": 1}, {"copy_id": 1, "member_id": 1, "due_at": "2030-01-01"}],
)
def test_loan_rejects_missing_and_client_controlled_fields(library, payload):
    assert library.client.post("/loans", json=payload).status_code == 400
    assert library.client.get("/loans").json == []


def test_loan_requires_valid_json(library):
    client = library.client
    assert client.post("/loans", data="copy_id=1").status_code == 415
    for body in ("{", "", "null"):
        assert client.post("/loans", data=body, content_type="application/json").status_code == 400
    assert client.get("/loans").json == []


def test_return_unknown_loan_and_reject_client_timestamp(library):
    client = library.client
    response = client.post("/loans/99/return")
    assert response.status_code == 404
    assert response.json["error"] == "loan_not_found"
    borrow(client)
    response = client.post("/loans/1/return", json={"returned_at": "2030-01-01"})
    assert response.status_code == 400
    assert client.get("/loans").json[0]["returned_at"] is None


def test_concurrent_requests_create_only_one_active_loan(library):
    def attempt(_):
        with library.app.test_client() as client:
            return borrow(client).status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(attempt, range(20)))
    assert statuses.count(201) == 1
    assert statuses.count(409) == 19
    assert len(library.client.get("/loans").json) == 1


def test_concurrent_returns_preserve_one_return_timestamp(library):
    borrow(library.client)
    library.clock.now += timedelta(days=1)

    def attempt(_):
        with library.app.test_client() as client:
            response = client.post("/loans/1/return")
            assert response.status_code == 200
            return response.json["returned_at"]

    with ThreadPoolExecutor(max_workers=4) as pool:
        timestamps = list(pool.map(attempt, range(10)))
    assert set(timestamps) == {library.clock.now.isoformat()}
    assert library.client.get("/copies").json[0]["status"] == "available"


def test_ui_shows_overdue_and_returned_loans(library):
    client = library.client
    borrow(client)
    library.clock.now += timedelta(days=29)
    page = client.get("/")
    assert page.status_code == 200
    assert "Überfällig" in page.text
    assert 'action="/loans/1/return"' in page.text
    assert 'value="2">Exemplar #2' in page.text
    assert 'value="1">Exemplar #1' not in page.text
    client.post("/loans/1/return")
    page = client.get("/")
    assert "Zurückgegeben:" in page.text
    assert 'action="/loans/1/return"' not in page.text
    assert 'value="1">Exemplar #1' in page.text
