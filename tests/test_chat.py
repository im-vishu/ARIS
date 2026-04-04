def _get_access_token(client):
    r = client.post("/v1/auth/token", json={"username": "vishu", "role": "user"})
    assert r.status_code == 200
    return r.json()["data"]["access_token"]


def test_chat_requires_auth(client):
    r = client.post("/v1/chat", json={"message": "hello"})
    assert r.status_code == 401


def test_chat_requires_message(client):
    token = _get_access_token(client)
    r = client.post("/v1/chat", headers={"Authorization": f"Bearer {token}"}, json={})
    assert r.status_code == 400


def test_chat_success(client):
    token = _get_access_token(client)
    r = client.post("/v1/chat", headers={"Authorization": f"Bearer {token}"}, json={"message": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["reply"].startswith("echo:")