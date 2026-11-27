"""`python -m ashfall_app.feedback list [--since DAYS]` prints what testers sent, oldest first, from the database
DATABASE_URL names."""
from datetime import UTC, datetime

import psycopg
import pytest

from ashfall_app.db.feedback import FeedbackRecord
from ashfall_app.feedback.__main__ import main, render


def plant(url: str) -> None:
    with psycopg.connect(url) as c:
        c.execute("INSERT INTO feedback (created_at, text, build, release, account_id, save_id, game_time, last_line) "
                  "VALUES (now() - interval '10 days', 'old words', 'main-aaa', 4, 1, 7, 900, 'l_old'), "
                  "(now() - interval '1 day', 'first line' || chr(10) || 'second line', 'main-bbb', 5, NULL, NULL, NULL, NULL)")


def test_lists_every_row_oldest_first_with_where_it_was(pg_url: str, monkeypatch: pytest.MonkeyPatch,
                                                        capsys: pytest.CaptureFixture[str]):
    plant(pg_url)
    monkeypatch.setenv("DATABASE_URL", pg_url)
    assert main(["list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 5, lines
    assert "build=main-aaa save=7 game_time=900 line=l_old" in lines[0] and lines[0].startswith("#")
    assert lines[1] == "    old words"
    assert "build=main-bbb save=- game_time=- line=-" in lines[2]
    assert lines[3:] == ["    first line", "    second line"]


def test_since_keeps_only_the_last_days_and_the_multiline_text_is_indented(pg_url: str, monkeypatch: pytest.MonkeyPatch,
                                                                           capsys: pytest.CaptureFixture[str]):
    plant(pg_url)
    monkeypatch.setenv("DATABASE_URL", pg_url)
    assert main(["list", "--since", "3"]) == 0
    out = capsys.readouterr().out
    assert "old words" not in out
    assert out.splitlines()[1:] == ["    first line", "    second line"]


def test_without_a_database_it_says_so(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert main(["list"]) == 2
    assert "DATABASE_URL" in capsys.readouterr().err


def test_a_control_character_in_the_words_is_shown_escaped_never_sent_to_the_terminal():
    now = datetime.now(UTC)
    words = "ok\x1b]52;c;AAAA\x07 \x1b[2J tab\there é\nnext\x9b"
    out = render(FeedbackRecord(1, now, words, "main-x", 5, None, None, None, None))
    assert out.splitlines()[1:] == ["    ok\\x1b]52;c;AAAA\\x07 \\x1b[2J tab\there é", "    next\\x9b"]
    assert not any(ch != "\n" and ch != "\t" and not ch.isprintable() for ch in out)
