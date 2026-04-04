def test_metrics_lite_exists(client):
    r = client.get("/v1/metrics-lite")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body