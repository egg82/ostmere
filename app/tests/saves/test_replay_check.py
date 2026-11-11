"""tools/replay_check.py on a dump built here: a log that says what was decided replays to a match from every snapshot;
one whose logged decision was moved mismatches from the snapshot before it, at the next checkpoint; rows stripped of
their manifest are read with the dump's manifests."""
from typing import Any

from ashfall_app import engine as e
from ashfall_app.db.manifests import stripped
from ashfall_app.engine.work import ready
from ashfall_app.saves.interface import Ruleset
from tools.replay_check import check_dump, report


def _dump(rs: Ruleset, broken: bool) -> dict[str, Any]:
    """Three taps of a card ready at the start, a snapshot after each of the first two, the row an hour on. Broken: the
    second tap is logged at 300, not 600."""
    s = e.new_save(rs.rules)
    card = next(c.id for c in rs.rules.cards if ready(s, rs.rules, c.id))
    dump: dict[str, Any] = {"saves": [], "snapshots": [], "decisions": []}
    for n, t in enumerate((0, 600, 1200), start=1):
        s = e.decide(s, rs.rules, t, e.TapCard(card))
        dump["decisions"].append({"save_id": 1, "n": n, "at": 300 if broken and n == 2 else t,
                                  "verb": e.verb_to_json(e.TapCard(card)), "rules_digest": rs.digest})
        if n < 3:
            dump["snapshots"].append({"save_id": 1, "day": 100 + n, "state": e.encode(s, rs.rules),
                                      "rules_digest": rs.digest, "decisions": n})
    s = e.advance(s, rs.rules, 4800)
    dump["saves"].append({"id": 1, "state": e.encode(s, rs.rules), "format": e.FORMAT, "rules_digest": rs.digest,
                          "decisions": 3, "game_time": s.time, "ended_at": None, "build": "b2", "release": rs.release})
    return dump


def test_an_honest_log_matches_from_every_snapshot(rs: Ruleset) -> None:
    found = check_dump(rs, _dump(rs, broken=False))
    (_, checks), = found
    assert [(c.day, c.match, c.first_diff_at) for c in checks] == [(101, True, None), (102, True, None)]
    assert report(found)[-1].startswith("summary saves=1 snapshots=2 mismatched_saves=0 ")


def test_a_changed_log_mismatches_at_the_next_checkpoint(rs: Ruleset) -> None:
    found = check_dump(rs, _dump(rs, broken=True))
    (_, checks), = found
    assert [(c.day, c.match) for c in checks] == [(101, False), (102, True)]
    assert (checks[0].first_diff_at, checks[0].last_match_at, checks[0].reason) == (600, 0, "snapshot")
    lines = report(found)
    assert lines[0] == "save=1 snapshot=101 match=false first_diff_at=600 last_match_at=0 crosses_release=false " \
                       "reason=snapshot"
    assert lines[2] == "save=1 mismatched_snapshots=1 ended=false ages_out_day=132 ages_out=1970-05-13"


def test_rows_stripped_of_their_manifest_are_read_with_the_dumps(rs: Ruleset) -> None:
    dump = _dump(rs, broken=False)
    manifest = stripped(dump["saves"][0]["state"])[1]
    for r in dump["saves"] + dump["snapshots"]:
        r["state"] = stripped(r["state"])[0]
    assert {c.reason for _, cs in check_dump(rs, dump) for c in cs} == {"unreadable"}   # control: no manifests, no read
    dump["manifests"] = [{"rules_digest": rs.digest, "manifest": manifest}]
    (_, checks), = check_dump(rs, dump)
    assert [(c.day, c.match) for c in checks] == [(101, True), (102, True)]
