def test_auth_token_success(client):
    r = client.post("/v1/auth/token", json={"username": "vishu", "role": "user"})
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


def test_auth_token_missing_username(client):
    r = client.post("/v1/auth/token", json={"role": "user"})
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == "bad_request"