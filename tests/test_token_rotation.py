def _login(client, username="vishu", role="user"):
    r = client.post("/v1/auth/token", json={"username": username, "role": role})
    assert r.status_code == 200
    return r.json()["data"]


def test_refresh_rotation_blocks_reuse(client):
    t = _login(client)
    refresh = t["refresh_token"]

    r1 = client.post("/v1/auth/refresh", json={"refresh_token": refresh})
    assert r1.status_code == 200

    r2 = client.post("/v1/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 401


def test_logout_revokes_refresh(client):
    t = _login(client)
    refresh = t["refresh_token"]

    r1 = client.post("/v1/auth/logout", json={"refresh_token": refresh})
    assert r1.status_code == 200

    r2 = client.post("/v1/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 401