def test_catalog_page_and_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert "Dein Katalog beginnt hier." in response.text
    assert 'id="book-form"' in response.text
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/catalog.js").status_code == 200


def test_catalog_shows_api_books_as_text(client):
    client.post("/books", json={"title": "<script>alert(1)</script>", "author": "A & B"})
    response = client.get("/")
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "<script>alert(1)</script>" not in response.text
    assert "A &amp; B" in response.text
    assert 'class="empty-state" hidden' in response.text


def test_member_and_copy_forms_have_empty_states(client):
    response = client.get("/")
    assert 'id="member-form"' in response.text
    assert 'id="copy-form"' in response.text
    assert "Noch keine Mitglieder erfasst." in response.text
    assert "Noch keine Exemplare erfasst." in response.text
    assert 'name="book_id" required disabled' in response.text


def test_page_displays_member_names_and_book_references_safely(client):
    client.post("/members", json={"name": "<script>member</script>"})
    book = client.post("/books", json={"title": "<b>Book</b>", "author": "A & B"}).json
    client.post("/copies", json={"book_id": book["id"]})
    response = client.get("/")
    assert "&lt;script&gt;member&lt;/script&gt;" in response.text
    assert "<script>member</script>" not in response.text
    assert "&lt;b&gt;Book&lt;/b&gt;" in response.text
    assert "<b>Book</b>" not in response.text
    assert 'Buch #1 · <span class="status-available">Verfügbar</span>' in response.text
    assert 'name="book_id" required disabled' not in response.text
