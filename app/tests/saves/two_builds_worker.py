"""One "pod" for tests/saves/test_two_builds.py: a process of its own playing saves under one build's rules against the
database ASHFALL_TEST_DB names. RULES picks today's opening (today) or a retune of it (retuned,
tests/saves/changes.py); RELEASE is its content release. Reads one JSON command a line on stdin, answers one JSON line on stdout:

    {"op": "create" | "advance" | "decide", "account": int, "save": int, "after": int, "now": iso}
    -> {"ok": true, "save": int, "decisions": int, "time": int} | {"ok": false, "error": "<exception class>"}"""
import json
import os
import sys
from datetime import datetime

from ashfall_app import engine as e
from ashfall_app.db.engine import open_database
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening
from ashfall_app.saves.interface import SaveError
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.service import PgSaves
from tests.saves.changes import retuned_opening


class Clock:
    now = datetime.fromisoformat("2026-10-01T12:00:00+00:00")

    def __call__(self) -> datetime:
        return self.now


def main() -> None:
    opening = retuned_opening() if os.environ["RULES"] == "retuned" else load_opening()
    rs = ruleset(opening, load_renames(), os.environ["BUILD_VERSION"], int(os.environ["RELEASE"]))
    clock = Clock()
    database = open_database(os.environ["ASHFALL_TEST_DB"], max_size=1)
    saves = PgSaves(database.engine, rs, clock)
    print(json.dumps({"ok": True, "ready": rs.build}), flush=True)
    for line in sys.stdin:
        cmd = json.loads(line)
        clock.now = datetime.fromisoformat(cmd["now"])
        try:
            if cmd["op"] == "create":
                _, played = saves.create(cmd["account"])
            elif cmd["op"] == "advance":
                played = saves.advance(cmd["account"], cmd["save"])
            else:
                played = saves.decide(cmd["account"], cmd["save"], e.TapCard(e.CardId("stand_up")), cmd["after"])
            out: dict[str, object] = {"ok": True, "save": played.save_id, "decisions": played.decisions,
                                      "time": played.save.time}
        except SaveError as ex:
            out = {"ok": False, "error": type(ex).__name__}
        print(json.dumps(out), flush=True)
    database.close()


if __name__ == "__main__":
    main()
