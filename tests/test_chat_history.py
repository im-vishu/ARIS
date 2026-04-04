def _token(client):
    r = client.post("/v1/auth/token", json={"username": "vishu", "role": "user"})
    assert r.status_code == 200
    return r.json()["data"]["access_token"]


def test_chat_persists_and_history_returns(client):
    t = _token(client)
    h = {"Authorization": f"Bearer {t}"}

    r1 = client.post("/v1/chat", headers=h, json={"message": "m1"})
    assert r1.status_code == 200

    r2 = client.post("/v1/chat", headers=h, json={"message": "m2"})
    assert r2.status_code == 200

    rh = client.get("/v1/chat/history?limit=20", headers=h)
    assert rh.status_code == 200
    items = rh.json()["data"]
    assert len(items) >= 2