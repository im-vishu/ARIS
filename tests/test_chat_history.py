def _token(client):
    r = client.post("/auth/token", json={"username": "vishu", "role": "user"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_chat_persists_and_history_returns(client):
    t = _token(client)

    r = client.post(
        "/chat",
        json={"message": "persist me"},
        headers={"Authorization": f"Bearer {t}"},
    )
    assert r.status_code == 200
    assert "message_id" in r.json()

    h = client.get(
        "/chat/history?limit=5",
        headers={"Authorization": f"Bearer {t}"},
    )
    assert h.status_code == 200
    data = h.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "message" in data[0]
    assert "reply" in data[0]