def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert body["total"] >= 1
    assert len(body["items"]) >= 1


def test_list_notes_pagination(client):
    for i in range(5):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    r = client.get("/notes/", params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) == 2
    assert body["total"] >= 5

    r = client.get("/notes/", params={"page": 3, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 3
    assert len(body["items"]) >= 1


def test_list_notes_pagination_empty_last_page(client):
    for i in range(3):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    r = client.get("/notes/", params={"page": 10, "page_size": 10})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert len(body["items"]) == 0


def test_list_notes_pagination_defaults(client):
    r = client.get("/notes/")
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 1
    assert body["page_size"] >= 1


def test_search_notes(client):
    client.post("/notes/", json={"title": "Hello", "content": "World"})
    client.post("/notes/", json={"title": "Foo", "content": "Bar"})

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_search_notes_no_results(client):
    r = client.get("/notes/search/", params={"q": "zzz_nonexistent_zzz"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0


def test_get_note_404(client):
    r = client.get("/notes/99999")
    assert r.status_code == 404


def test_create_note_validation(client):
    r = client.post("/notes/", json={"title": "", "content": ""})
    assert r.status_code == 422

    r = client.post("/notes/", json={})
    assert r.status_code == 422
