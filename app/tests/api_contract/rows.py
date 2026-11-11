"""What HTTP cannot reach, reached in the test's own database: the wall clock (a save's or a session's age), a save a
newer build wrote, a rate count already spent. Names are the schema's at the contract commit (db/tables.py). Each test
has a database of its own, so a helper that touches every row of a table touches only that test's."""
import json
from typing import Any, LiteralString

import psycopg


def scalar(url: str, query: LiteralString, *args: object) -> Any:
    with psycopg.connect(url) as c:
        row = c.execute(query, args).fetchone()
    assert row is not None
    return row[0]


def run(url: str, query: LiteralString, *args: object) -> int:
    with psycopg.connect(url) as c:
        return c.execute(query, args).rowcount


def count(url: str, table: LiteralString) -> int:
    return int(scalar(url, f"SELECT count(*) FROM {table}"))


def age_saves(url: str, seconds: int) -> None:
    """Every save began, and was last written, `seconds` earlier (negative: later) than it was."""
    n = run(url, "UPDATE saves SET created_at = created_at - make_interval(secs => %s), "
                 "started_at = started_at - make_interval(secs => %s), updated_at = updated_at - make_interval(secs => %s)",
            seconds, seconds, seconds)
    assert n > 0, "no save to age"


def age_sessions(url: str, days: int) -> None:
    n = run(url, "UPDATE sessions SET created_at = now() - make_interval(days => %s), "
                 "last_seen_at = now() - make_interval(days => %s)", days, days)
    assert n > 0, "no session to age"


def session_last_seen_age_s(url: str) -> float:
    return float(scalar(url, "SELECT extract(epoch FROM now() - max(last_seen_at)) FROM sessions"))


def the_save_row(url: str) -> tuple[Any, ...]:
    """The one save in the database, every column: what `nothing is written` compares."""
    with psycopg.connect(url) as c:
        rows = c.execute("SELECT * FROM saves").fetchall()
    assert len(rows) == 1, f"{len(rows)} saves, expected one"
    return tuple(rows[0])


def whole_state(url: str) -> str:
    """The one save's state with its manifest: a row stored without it is read with its digest's in save_manifests."""
    with psycopg.connect(url) as c:
        found = c.execute("SELECT s.state, m.manifest FROM saves s "
                          "LEFT JOIN save_manifests m ON m.rules_digest = s.rules_digest").fetchall()
    assert len(found) == 1, f"{len(found)} saves, expected one"
    state, manifest = found[0]
    envelope: dict[str, Any] = json.loads(state)
    if "manifest" in envelope:
        return str(state)
    assert manifest is not None, "the save is stored without its manifest and none is held for its digest"
    envelope["manifest"] = json.loads(manifest)
    return json.dumps(envelope, sort_keys=True, separators=(",", ":"))


def from_a_newer_build(url: str) -> None:
    """The one save, as a build with a newer state format wrote it: the format no build here can read or rebase."""
    state = whole_state(url)
    envelope: dict[str, Any] = json.loads(state)
    assert isinstance(envelope.get("format"), int), "the state is not the envelope this tamper knows"
    envelope["format"] += 1000
    newer = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
    assert run(url, "UPDATE saves SET state = %s, format = format + 1000", newer) == 1


def under_older_rules(url: str) -> str:
    """The one save, with only its rules digest changed (the rules an older build released). The state stays its
    canonical encoding (asserted), so a rebase can carry it; returns the digest planted."""
    state = whole_state(url)
    envelope: dict[str, Any] = json.loads(state)
    assert json.dumps(envelope, sort_keys=True, separators=(",", ":")) == state, "the state is not canonical JSON"
    assert isinstance(envelope.get("rules"), str), "the envelope's rules are not a digest"
    old = "0" * len(envelope["rules"])
    envelope["rules"] = old
    assert run(url, "UPDATE saves SET state = %s, rules_digest = %s",
               json.dumps(envelope, sort_keys=True, separators=(",", ":")), old) == 1
    return old
