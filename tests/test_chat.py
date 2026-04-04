def _get_access_token(client):
    r = client.post("/auth/token", json={"username": "vishu", "role": "user"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_chat_requires_auth(client):
    r = client.post("/chat", json={"message": "hello"})
    assert r.status_code == 401


def test_chat_requires_message(client):
    token = _get_access_token(client)
    r = client.post("/chat", json={"message": ""}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400


def test_chat_success(client):
    token = _get_access_token(client)
    r = client.post("/chat", json={"message": "hello"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "reply" in r.json()