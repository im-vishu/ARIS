def test_metrics_lite_exists(client):
    r = client.get("/metrics-lite")
    assert r.status_code == 200
    body = r.json()
    assert "requests_total" in body
    assert "errors_total" in body
    assert "chat_requests_total" in body