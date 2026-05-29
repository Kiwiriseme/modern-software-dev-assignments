def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert body["total"] >= 1


def test_list_action_items_pagination(client):
    for i in range(5):
        client.post("/action-items/", json={"description": f"Task {i}"})

    r = client.get("/action-items/", params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) == 2
    assert body["total"] >= 5

    r = client.get("/action-items/", params={"page": 3, "page_size": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["page"] == 3
    assert len(body["items"]) >= 1


def test_list_action_items_empty_page(client):
    r = client.get("/action-items/", params={"page": 100, "page_size": 10})
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 0
    assert body["total"] >= 0


def test_complete_action_item_404(client):
    r = client.put("/action-items/99999/complete")
    assert r.status_code == 404


def test_create_action_item_validation(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422

    r = client.post("/action-items/", json={})
    assert r.status_code == 422
