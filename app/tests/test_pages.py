"""The page the visitor is served (ashfall_app/web/page.py): what it loads, and the small documents beside it."""

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from ashfall_app.page_config import page_config
from ashfall_app.web import app as web
from ashfall_app.web import og

UMAMI = "https://stats.example/script.js"
FOREIGN = re.compile(r"(?:https?:)?//([\w-]+(?:\.[\w-]+)+)")   # an absolute or protocol-relative address: its host


def foreign_origins(text: str, allowed: set[str]) -> set[str]:
    """Every host the text names that is not in `allowed`; the visitor's browser would send it their address."""
    return {host for host in FOREIGN.findall(text) if host not in allowed}


def test_the_origin_probe_sees_a_foreign_host_and_lets_the_configured_one_pass():
    html = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X"><img src="//cdn.example/a.png">'
    assert foreign_origins(html, set()) == {"fonts.googleapis.com", "cdn.example"}
    assert foreign_origins(html, {"cdn.example"}) == {"fonts.googleapis.com"}
    assert foreign_origins("<a href='/privacy'>x</a> // a comment", set()) == set()


def test_the_shell_names_no_origin_but_its_own_and_the_configured_tracker():
    """Fonts, scripts and styles come from this app: a third-party address in the page tells that host every visitor's
    IP. The tracker's script is added by the page from page-config.json (telemetry.ts), never written into the shell."""
    config = page_config({"ASHFALL_UMAMI_SCRIPT_URL": UMAMI, "ASHFALL_UMAMI_WEBSITE_ID": "site"})
    assert config.umami is not None
    allowed = {urlparse(config.umami.script_url).hostname or "", urlparse(og.SITE_URL).hostname or ""}   # the preview tags name the site itself
    shell = TestClient(web.create_app()).get("/")
    assert shell.status_code == 200 and "<title>The Breaking of Ostmere</title>" in shell.text
    assert foreign_origins(shell.text, allowed) == set()


PAGES = ["/", "/privacy"]
FONT_FILES = re.findall(r"url\(([\w.-]+)\)", (Path(__file__).parent.parent / "ashfall_app" / "static" / "fonts" / "fonts.css").read_text())


def test_the_fonts_every_page_uses_are_served_by_the_app():
    client = TestClient(web.create_app())
    for page in PAGES:
        text = client.get(page).text
        assert "/fonts/fonts.css" not in text and text.count("@font-face") == 4, page   # inline: no request blocks the paint
        assert re.findall(r"url\((/fonts/[\w.-]+)\)", text) == [f"/fonts/{n}" for n in FONT_FILES], page
    css = client.get("/fonts/fonts.css")
    assert css.status_code == 200 and css.headers["content-type"].startswith("text/css")
    declared = re.findall(r"url\(([\w.-]+)\)", css.text)
    assert declared == FONT_FILES   # Alegreya Sans (two), IM Fell English SC and the journal's hand
    for name in declared:
        got = client.get(f"/fonts/{name}")
        assert got.status_code == 200 and got.headers["content-type"] == "font/woff2" and got.content[:4] == b"wOF2", name


def test_the_privacy_page_is_html_in_the_games_look_and_names_no_foreign_origin():
    got = TestClient(web.create_app()).get("/privacy")
    assert got.status_code == 200 and got.headers["content-type"].startswith("text/html")
    assert "<title>Privacy · The Breaking of Ostmere</title>" in got.text and "__Host-ashfall_session" in got.text
    assert "IM Fell English SC" in got.text and "#0d0e10" in got.text
    assert foreign_origins(got.text, set()) == set()


def test_robots_txt_allows_everything_but_the_api():
    got = TestClient(web.create_app()).get("/robots.txt")
    assert got.status_code == 200 and got.headers["content-type"].startswith("text/plain")
    lines = [line for line in got.text.splitlines() if line]
    assert lines == ["User-agent: *", "Disallow: /api/"]


def test_llms_txt_names_the_game_and_links_the_play_and_privacy_pages():
    got = TestClient(web.create_app()).get("/llms.txt")
    assert got.status_code == 200 and got.headers["content-type"].startswith("text/plain")
    lines = got.text.splitlines()
    assert lines[0] == "# The Breaking of Ostmere" and lines[2].startswith("> ")
    links = re.findall(r"^- \[[^\]]+\]\(([^)]+)\)", got.text, re.M)
    assert links == ["https://ostmere.yggdrasil.pub/", "https://ostmere.yggdrasil.pub/privacy"]


def test_the_shell_links_the_privacy_page_in_a_tab_of_its_own():
    shell = TestClient(web.create_app()).get("/").text
    link = re.search(r'<a [^>]*href="/privacy"[^>]*>', shell)
    assert link is not None
    assert 'target="_blank"' in link.group(0) and 'rel="noopener"' in link.group(0)


class HeadMeta(HTMLParser):
    """The <meta> tags of a page, keyed by their property or name."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        key = a.get("property") or a.get("name")
        if tag == "meta" and key:
            self.tags[key] = a.get("content") or ""


def head_meta(html: str) -> dict[str, str]:
    parser = HeadMeta()
    parser.feed(html.split("</head>")[0])
    return parser.tags


TAGLINE = "The world ended. The chores didn't."
PREVIEW_TAGS = {
    "og:type": "website", "og:site_name": "The Breaking of Ostmere", "og:title": "The Breaking of Ostmere",
    "og:url": "https://ostmere.yggdrasil.pub/", "og:description": TAGLINE, "description": TAGLINE,
    "og:image:width": "1200", "og:image:height": "630", "twitter:card": "summary_large_image",
}


def missing_preview_tags(tags: dict[str, str]) -> list[str]:
    wrong = [k for k, v in PREVIEW_TAGS.items() if tags.get(k) != v]
    wrong += [k for k in ("og:image", "og:image:alt") if not tags.get(k)]
    image = urlparse(tags.get("og:image", ""))
    return wrong + ([] if image.scheme == "https" and image.netloc else ["og:image absolute"])


def front_page(monkeypatch: pytest.MonkeyPatch, assets: Path) -> str:
    monkeypatch.setenv("ASSETS_DIR", str(assets))
    return TestClient(web.create_app()).get("/").text


def test_the_preview_check_names_a_tag_the_head_lacks():
    tags = {**PREVIEW_TAGS, "og:image": "https://x.example/c.png", "og:image:alt": "a camp"}
    assert missing_preview_tags(tags) == []
    for key in PREVIEW_TAGS:
        assert missing_preview_tags({k: v for k, v in tags.items() if k != key}) == [key]
    assert missing_preview_tags({**tags, "og:image": "/assets/c.png"}) == ["og:image absolute"]


def test_the_front_page_head_carries_every_preview_tag_with_an_absolute_image(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    tags = head_meta(front_page(monkeypatch, tmp_path))
    assert missing_preview_tags(tags) == []
    assert tags["og:image"] == f"https://ostmere.yggdrasil.pub/assets/{og.CARD_PATH}"   # no card seeded yet: still absolute


def test_the_cards_address_changes_with_its_bytes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    card = tmp_path / og.CARD_PATH
    card.parent.mkdir(parents=True)
    seen: list[str] = []
    for body in (b"first card", b"second card!"):
        card.write_bytes(body)
        seen.append(head_meta(front_page(monkeypatch, tmp_path))["og:image"])
    assert len(set(seen)) == 2
    assert all(urlparse(u).path == f"/assets/{og.CARD_PATH}" and len(parse_qs(urlparse(u).query)["h"][0]) == 12 for u in seen)
    served = TestClient(web.create_app()).get(f"/assets/{og.CARD_PATH}?h={parse_qs(urlparse(seen[-1]).query)['h'][0]}")
    assert served.content == b"second card!" and "immutable" in served.headers["cache-control"]   # the address is the one it keeps for good
