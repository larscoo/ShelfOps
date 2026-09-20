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
