"""The old host's 301 to the new one (ashfall_app/old_host.py), and that both servers wire it."""

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ashfall_app.main import create_app as app_server
from ashfall_app.old_host import OldHostRedirect, old_hosts
from ashfall_app.web.app import create_app as web_server

OLD = "ashfall.yggdrasil.pub"
NEW = "https://ostmere.yggdrasil.pub"


def inner() -> FastAPI:
    app = FastAPI()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


def client(host: str) -> TestClient:
    return TestClient(OldHostRedirect(inner(), frozenset({OLD})), base_url=f"http://{host}", follow_redirects=False)


def test_old_host_redirects_keeping_path_and_query() -> None:
    r = client(OLD).get("/api/games/a%20b?x=1&y=%2F")
    assert r.status_code == 301
    assert r.headers["location"] == NEW + "/api/games/a%20b?x=1&y=%2F"


def test_old_host_redirects_the_root_without_a_query() -> None:
    r = client(OLD.upper()).post("/")
    assert (r.status_code, r.headers["location"]) == (301, NEW + "/")


@pytest.mark.parametrize("host", ["ostmere.yggdrasil.pub", "10.1.2.3", "10.1.2.3:8000", "x." + OLD, OLD + ".evil.example"])
def test_other_hosts_pass(host: str) -> None:
    r = client(host).get("/healthz")
    assert (r.status_code, r.json()) == (200, {"status": "ok"})


def test_a_request_with_no_host_passes() -> None:
    sent: list[Any] = []

    async def downstream(scope: Any, receive: Any, send: Any) -> None:
        sent.append(scope["path"])

    import asyncio

    scope: dict[str, Any] = {"type": "http", "path": "/healthz", "headers": [], "query_string": b""}
    asyncio.run(OldHostRedirect(downstream, frozenset({OLD}))(scope, None, None))
    assert sent == ["/healthz"]


def test_old_hosts_come_from_config_with_a_default() -> None:
    assert old_hosts({}) == {OLD}
    assert old_hosts({"ASHFALL_OLD_HOSTS": "A.example, b.example,"}) == {"a.example", "b.example"}


@pytest.mark.parametrize("make", [app_server, web_server], ids=["app", "web"])
def test_both_servers_redirect_the_old_host(make: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ASHFALL_OLD_HOSTS", raising=False)
    c = TestClient(make(), base_url=f"http://{OLD}", follow_redirects=False)
    r = c.get("/healthz?probe=1")
    assert (r.status_code, r.headers["location"]) == (301, NEW + "/healthz?probe=1")
    ok = TestClient(make(), base_url="http://10.0.0.7:8000", follow_redirects=False).get("/healthz")
    assert ok.status_code != 301
