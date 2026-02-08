from backend.app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_reciters_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/reciters")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 10
    assert {"id", "name", "audio_base_url"}.issubset(data[0].keys())


def test_status_endpoint_missing_job():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/status/missing")
    assert response.status_code == 404
    assert response.get_json()["status"] == "not_found"
