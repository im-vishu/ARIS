def test_health_ok(client):
    r = client.get("/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["status"] == "ok"


def test_ready_exists(client):
    r = client.get("/v1/ready")
    assert r.status_code in (200, 503)