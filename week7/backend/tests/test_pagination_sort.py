def test_skip_limit_pagination(client):
    ids = []
    for i in range(5):
        r = client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])

    r = client.get("/notes/", params={"skip": 0, "limit": 2})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 2

    r = client.get("/notes/", params={"skip": 2, "limit": 2})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 2

    r = client.get("/notes/", params={"skip": 4, "limit": 2})
    assert r.status_code == 200
    page3 = r.json()
    assert len(page3) == 1

    page1_ids = {item["id"] for item in page1}
    page2_ids = {item["id"] for item in page2}
    page3_ids = {item["id"] for item in page3}
    assert page1_ids.isdisjoint(page2_ids)
    assert page1_ids.isdisjoint(page3_ids)
    assert page2_ids.isdisjoint(page3_ids)
    assert page1_ids | page2_ids | page3_ids == set(ids)


def test_sort_by_title_asc(client):
    for title in ("C", "A", "B"):
        r = client.post("/notes/", json={"title": title, "content": "x"})
        assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    titles = [item["title"] for item in r.json()]
    assert titles == ["A", "B", "C"]


def test_sort_by_title_desc(client):
    for title in ("C", "A", "B"):
        r = client.post("/notes/", json={"title": title, "content": "x"})
        assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    titles = [item["title"] for item in r.json()]
    assert titles == ["C", "B", "A"]


def test_invalid_sort_field_falls_back_to_created_at_desc(client):
    r = client.post("/notes/", json={"title": "Test", "content": "Hello"})
    assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"sort": "nonexistent_field"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_action_items_pagination_and_sort(client):
    for desc in ("Zeta", "Alpha", "Gamma", "Beta"):
        r = client.post("/action-items/", json={"description": desc})
        assert r.status_code == 201, r.text

    r = client.get("/action-items/", params={"skip": 1, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2

    r = client.get("/action-items/", params={"sort": "description"})
    assert r.status_code == 200
    descriptions = [item["description"] for item in r.json()]
    assert descriptions == sorted(descriptions)


def test_search_with_pagination(client):
    for i in range(4):
        r = client.post("/notes/", json={"title": f"Alpha {i}", "content": "Shared keyword"})
        assert r.status_code == 201, r.text
    r = client.post("/notes/", json={"title": "Unrelated", "content": "Nothing here"})
    assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"q": "Shared", "skip": 0, "limit": 2})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 2

    r = client.get("/notes/", params={"q": "Shared", "skip": 2, "limit": 2})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 2

    ids1 = {item["id"] for item in page1}
    ids2 = {item["id"] for item in page2}
    assert ids1.isdisjoint(ids2)


def test_skip_past_end_returns_empty(client):
    r = client.post("/notes/", json={"title": "Only", "content": "One"})
    assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"skip": 10, "limit": 5})
    assert r.status_code == 200
    assert r.json() == []


def test_default_sort_is_created_at_desc(client):
    r1 = client.post("/notes/", json={"title": "First", "content": "a"})
    assert r1.status_code == 201, r1.text
    r2 = client.post("/notes/", json={"title": "Second", "content": "b"})
    assert r2.status_code == 201, r2.text

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2
    created_ats = [item["created_at"] for item in items]
    assert created_ats == sorted(created_ats, reverse=True)


def test_action_items_completed_filter_with_pagination(client):
    for desc in ("Task A", "Task B", "Task C"):
        r = client.post("/action-items/", json={"description": desc})
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        if desc in ("Task A", "Task B"):
            client.put(f"/action-items/{rid}/complete")

    r = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "skip": 1, "limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["completed"] is True
