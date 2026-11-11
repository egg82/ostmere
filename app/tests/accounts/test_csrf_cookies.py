"""The HTTP side of accounts: the CSRF guard on writes under /api/, and cookies queued from anywhere in a request."""
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from ashfall_app.accounts import cookies
from ashfall_app.accounts.csrf import CsrfMiddleware, body_ok, origin_ok


def guarded() -> TestClient:
    app = FastAPI()

    @app.post("/api/thing")
    def thing() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/elsewhere")
    def elsewhere() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/api/thing")
    def read() -> dict[str, bool]:
        return {"ok": True}

    app.add_middleware(CsrfMiddleware)
    return TestClient(app, base_url="https://ashfall.test")


def test_a_write_from_this_site_goes_through():
    c = guarded()
    assert c.post("/api/thing", json={}, headers={"Origin": "https://ashfall.test"}).status_code == 200
    assert c.post("/api/thing", json={}, headers={"Sec-Fetch-Site": "same-origin"}).status_code == 200
    assert c.post("/api/thing", json={}, headers={"Sec-Fetch-Site": "none"}).status_code == 200


def test_a_write_from_another_site_is_refused_as_cross_site():
    c = guarded()
    for headers in ({"Origin": "https://evil.test"}, {"Origin": "null"}, {"Sec-Fetch-Site": "cross-site"},
                    {"Sec-Fetch-Site": "same-site"}, {"Origin": "https://ashfall.test.evil.test"},
                    {"Origin": "http://ashfall.test"}, {}):
        r = c.post("/api/thing", json={}, headers=headers)
        assert r.status_code == 403 and r.json() == {"code": "cross_site", "message": r.json()["message"], "step": None}, headers


def test_a_body_that_is_not_json_is_refused():
    c = guarded()
    c.headers["Origin"] = "https://ashfall.test"
    r = c.post("/api/thing", content=b"a=1", headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert r.status_code == 415 and r.json()["code"] == "not_json"
    r = c.post("/api/thing", content=b"{}", headers={"Content-Type": "text/plain"})
    assert r.status_code == 415
    assert c.post("/api/thing", content=b"{}", headers={"Content-Type": "application/json; charset=utf-8"}).status_code == 200


def test_reads_and_paths_outside_the_api_are_not_guarded():
    c = guarded()
    assert c.get("/api/thing", headers={"Origin": "https://evil.test"}).status_code == 200
    assert c.post("/elsewhere", content=b"x", headers={"Origin": "https://evil.test", "Content-Type": "text/plain"}).status_code == 200


def test_the_checks_alone():
    assert origin_ok({"origin": "https://a.test", "host": "a.test"}) and not origin_ok({"origin": "https://b.test", "host": "a.test"})
    assert origin_ok({"origin": "https://A.test", "host": "a.TEST"})
    assert not origin_ok({"origin": "http://a.test", "host": "a.test"}) and not origin_ok({"origin": "null", "host": "null"})
    assert body_ok({}) and not body_ok({"content-length": "3"}) and body_ok({"content-length": "0", "content-type": "text/plain"}) is False


def test_a_queued_cookie_is_set_on_the_response_with_its_attributes_and_reads_back():
    app = FastAPI()
    app.add_middleware(cookies.CookieMiddleware)

    @app.get("/set")
    def set_it(request: Request) -> dict[str, str | None]:
        cookies.queue(request, cookies.SESSION, "tok", 400 * 86400)
        return {"read": cookies.read(request, cookies.SESSION)}

    @app.get("/read")
    def read_it(request: Request) -> dict[str, str | None]:
        return {"read": cookies.read(request, cookies.SESSION)}

    c = TestClient(app, base_url="https://ashfall.test")
    r = c.get("/set")
    assert r.json() == {"read": "tok"}
    header = r.headers["set-cookie"]
    for part in ("__Host-ashfall_session=tok", "Max-Age=34560000", "Path=/", "Secure", "HttpOnly", "SameSite=None",
                 "Partitioned"):
        assert part in header, part
    assert "Domain" not in header
    assert c.get("/read").json() == {"read": "tok"}   # the browser sends it back
    assert TestClient(app, base_url="https://ashfall.test").get("/read").json() == {"read": None}


def test_of_two_session_cookies_the_last_one_sent_is_the_session():
    """A browser that held the cookie before it was Partitioned holds two of that name, and sends the older first
    (RFC 6265 5.4, by creation time; Chromium does, Firefox keeps one): the newer, partitioned one is the session."""
    app = FastAPI()
    app.add_middleware(cookies.CookieMiddleware)

    @app.get("/read")
    def read_it(request: Request) -> dict[str, str | None]:
        return {"read": cookies.read(request, cookies.SESSION)}

    sent = {"Cookie": f"{cookies.SESSION}=older; {cookies.SESSION}=newer"}
    assert TestClient(app, base_url="https://ashfall.test").get("/read", headers=sent).json() == {"read": "newer"}
