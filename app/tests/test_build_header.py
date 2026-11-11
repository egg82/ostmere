"""Every response names the build that answered (X-Ashfall-Build, api/CONTRACT.txt), errors included."""
import pytest
from fastapi.testclient import TestClient

from ashfall_app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("BUILD_VERSION", "main-abc-1")
        app = create_app()

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("planted")

    return TestClient(app, raise_server_exceptions=False, headers={"Origin": "https://testserver"})


@pytest.mark.parametrize(("method", "path", "body", "status"), [
    ("GET", "/healthz", None, 200),
    ("GET", "/", None, 200),
    ("GET", "/page-config.json", None, 200),
    ("GET", "/api/content", None, 200),
    ("GET", "/api/me", None, 503),   # no database here: who is asking cannot be told
    ("POST", "/api/saves", None, 503),   # no database here: save_unavailable
    ("POST", "/api/saves/1/advance", None, 503),
    ("POST", "/api/saves/1/decisions", {"decision": {"kind": "nope"}, "after": 0}, 422),
    ("GET", "/no/such/path", None, 404),
    ("GET", "/boom", None, 500),
])
def test_every_answer_names_the_build(client: TestClient, method: str, path: str, body: object, status: int):
    r = client.request(method, path, json=body)
    assert r.status_code == status, r.text
    assert r.headers.get("x-ashfall-build") == "main-abc-1"
    assert len(r.headers.get_list("x-ashfall-build")) == 1
    assert r.headers.get_list("x-ashfall-server") == ["app"]
