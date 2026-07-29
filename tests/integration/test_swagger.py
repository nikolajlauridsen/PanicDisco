from disco_server import create_app


def test_apispec_json_documents_the_tracks_routes(tmp_path):
    app = create_app({"DATABASE_PATH": str(tmp_path / "test.db")})

    response = app.test_client().get("/apispec_1.json")

    assert response.status_code == 200
    spec = response.get_json()
    assert spec["swagger"] == "2.0"
    assert spec["info"]["title"] == "PanicDisco API"
    assert "get" in spec["paths"]["/api/tracks"]
    assert "get" in spec["paths"]["/api/tracks/{track_id}"]
    assert "put" in spec["paths"]["/api/tracks/{track_id}"]
    assert "delete" in spec["paths"]["/api/tracks/{track_id}"]


def test_apidocs_ui_is_served(tmp_path):
    app = create_app({"DATABASE_PATH": str(tmp_path / "test.db")})

    response = app.test_client().get("/apidocs/")

    assert response.status_code == 200
