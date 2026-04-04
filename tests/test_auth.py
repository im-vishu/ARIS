def test_auth_token_success(client):
    r = client.post("/auth/token", json={"username": "vishu", "role": "user"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_auth_token_missing_username(client):
    r = client.post("/auth/token", json={"role": "user"})
    assert r.status_code == 400