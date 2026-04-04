def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_exists(client):
    r = client.get("/ready")
    # can be 200 or 503 depending on env/dependencies
    assert r.status_code in (200, 503)
    body = r.json()
    assert "status" in body
    assert "checks" in body
    assert "redis" in body["checks"]
    assert "openai_key" in body["checks"]