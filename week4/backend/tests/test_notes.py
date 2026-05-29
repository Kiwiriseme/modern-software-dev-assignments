def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_note(client):
    payload = {"title": "Old", "content": "Old content"}
    r = client.post("/notes/", json=payload)
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "New", "content": "New content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "New"
    assert data["content"] == "New content"


def test_update_note_partial(client):
    payload = {"title": "Old", "content": "Old content"}
    r = client.post("/notes/", json=payload)
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Renamed"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Renamed"
    assert data["content"] == "Old content"


def test_update_note_not_found(client):
    r = client.put("/notes/9999", json={"title": "X"})
    assert r.status_code == 404


def test_delete_note(client):
    payload = {"title": "ToDelete", "content": "Bye"}
    r = client.post("/notes/", json=payload)
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


def test_create_note_validation_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "ok"})
    assert r.status_code == 422


def test_create_note_validation_empty_content(client):
    r = client.post("/notes/", json={"title": "ok", "content": ""})
    assert r.status_code == 422


def test_update_note_validation_empty_title(client):
    payload = {"title": "X", "content": "Y"}
    r = client.post("/notes/", json=payload)
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": ""})
    assert r.status_code == 422


def test_get_note_not_found(client):
    r = client.get("/notes/9999")
    assert r.status_code == 404
