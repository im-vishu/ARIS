def _token(client, username: str, role: str = "user"):
    r = client.post("/v1/auth/token", json={"username": username, "role": role})
    assert r.status_code == 200
    return r.json()["data"]["access_token"]


def test_history_requires_auth(client):
    r = client.get("/v1/chat/history")
    assert r.status_code == 401


def test_user_history_is_isolated(client):
    t1 = _token(client, "alice", "user")
    t2 = _token(client, "bob", "user")

    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}

    assert client.post("/v1/chat", headers=h1, json={"message": "alice-msg"}).status_code == 200
    assert client.post("/v1/chat", headers=h2, json={"message": "bob-msg"}).status_code == 200

    r1 = client.get("/v1/chat/history", headers=h1)
    r2 = client.get("/v1/chat/history", headers=h2)

    assert r1.status_code == 200
    assert r2.status_code == 200

    alice_items = r1.json()["data"]
    bob_items = r2.json()["data"]

    assert all(i["username"] == "alice" for i in alice_items)
    assert all(i["username"] == "bob" for i in bob_items)


def test_admin_can_view_all_history(client):
    t_user = _token(client, "charlie", "user")
    t_admin = _token(client, "admin1", "admin")

    h_user = {"Authorization": f"Bearer {t_user}"}
    h_admin = {"Authorization": f"Bearer {t_admin}"}

    assert client.post("/v1/chat", headers=h_user, json={"message": "charlie-msg"}).status_code == 200

    r = client.get("/v1/chat/history?limit=50", headers=h_admin)
    assert r.status_code == 200
    items = r.json()["data"]
    assert any(i["username"] == "charlie" for i in items)