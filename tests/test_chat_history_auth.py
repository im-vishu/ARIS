def _token(client, username: str, role: str = "user"):
    r = client.post("/auth/token", json={"username": username, "role": role})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_history_requires_auth(client):
    r = client.get("/chat/history")
    assert r.status_code == 401


def test_user_history_is_isolated(client):
    t1 = _token(client, "alice", "user")
    t2 = _token(client, "bob", "user")

    r1 = client.post("/chat", json={"message": "hello from alice"}, headers={"Authorization": f"Bearer {t1}"})
    assert r1.status_code == 200

    r2 = client.post("/chat", json={"message": "hello from bob"}, headers={"Authorization": f"Bearer {t2}"})
    assert r2.status_code == 200

    h_alice = client.get("/chat/history?limit=20", headers={"Authorization": f"Bearer {t1}"})
    assert h_alice.status_code == 200
    msgs_alice = [x["message"] for x in h_alice.json()]
    assert any("hello from alice" == m for m in msgs_alice)
    assert all(m != "hello from bob" for m in msgs_alice)

    h_bob = client.get("/chat/history?limit=20", headers={"Authorization": f"Bearer {t2}"})
    assert h_bob.status_code == 200
    msgs_bob = [x["message"] for x in h_bob.json()]
    assert any("hello from bob" == m for m in msgs_bob)
    assert all(m != "hello from alice" for m in msgs_bob)


def test_admin_can_view_all_history(client):
    t_user = _token(client, "charlie", "user")
    t_admin = _token(client, "root-admin", "admin")

    r = client.post("/chat", json={"message": "visible to admin"}, headers={"Authorization": f"Bearer {t_user}"})
    assert r.status_code == 200

    h_admin = client.get("/chat/history?limit=50", headers={"Authorization": f"Bearer {t_admin}"})
    assert h_admin.status_code == 200
    msgs = [x["message"] for x in h_admin.json()]
    assert "visible to admin" in msgs