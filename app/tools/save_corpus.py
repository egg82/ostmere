"""Saves from playthrough checkpoints, written as encoded texts: the golden saves, and the CI job saves-forward's input.

    python tools/save_corpus.py <dir>            # write NN-seed-time.json, one encoded save each, under this commit's rules
    python tools/save_corpus.py --load <dir>     # rebase each under this commit's rules and renames, advance it 30 days

With DATABASE_URL set, --load goes the way a player's save does: each is stored as a row (migrating that database
first), the app's start check runs over them, and each is opened through the saves service 30 days after it was last
written, so rebased at load and advanced to now by the server's clock. Run from app/. The golden saves (tests/saves/golden/f<FORMAT>/) are this tool's output and nothing else's; the
saves-forward job writes them at the commit before a push and loads them with the commit pushed, so a format upgrade or
a rebase that breaks a save of the opening's depth goes red before it deploys (engine DESIGN.txt, "Rebase"). They go no
deeper than the opening's end: the release lock holds the ids of every later chapter.
"""
import json
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from ashfall_app import logs
from ashfall_app.db import accounts
from ashfall_app.db import saves as rows
from ashfall_app.db.engine import open_database
from ashfall_app.db.migrate import migrate
from ashfall_app.engine import Rules, Save, advance, encode, new_save, rebase
from ashfall_app.opening.lock import load_lock
from ashfall_app.saves.check import check
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.service import PgSaves
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import load_opening, to_rules
from tests.opening.playthrough import Player

SEEDS = (0, 1, 2)
STOPS = (45, 120, 240, 400)
"""Game seconds a checkpoint is taken at (the opening's end follows them): story steps, the rack, the first mix,
orders and rests."""
DAY_S = 86_400


def checkpoints(rules: Rules) -> list[tuple[str, Save]]:
    """A new game, then each seed's player at each stop and at the end."""
    found = [("new", new_save(rules))]
    for seed in SEEDS:
        p = Player(rules, seed)
        for stop in STOPS:
            p.play_until(lambda: p.end_at is not None or p.save.time >= stop)
            found.append((f"seed{seed}-t{p.save.time}", p.save))
        p.play()
        found.append((f"seed{seed}-end{p.save.time}", p.save))
    return found


def write(out: Path) -> int:
    rules = to_rules(load_opening())
    out.mkdir(parents=True, exist_ok=True)
    written: set[str] = set()
    for i, (name, save) in enumerate(checkpoints(rules)):
        text = encode(save, rules)
        if text in written:
            continue
        written.add(text)
        (out / f"{i:02d}-{name}.json").write_text(text + "\n")
    print(f"event=save_corpus.write saves={len(written)} dir={out}")
    return 0


def load(src: Path, days: int = 30) -> int:
    """Each save rebased under this commit's rules and advanced `days` game days; 1 if any fails."""
    rules, renames = to_rules(load_opening()), engine_renames(load_renames())
    failed = 0
    paths = sorted(src.glob("*.json"))
    for path in paths:
        started = time.perf_counter()
        try:
            save = rebase(path.read_text().strip(), rules, renames)
            advance(save, rules, save.time + days * DAY_S)
        except Exception as e:   # report every save, not only the first that fails
            failed += 1
            print(f"event=save_corpus.failed save={path.name} error={type(e).__name__} message={e!s:.200}")
            continue
        print(f"event=save_corpus.loaded save={path.name} ms={int((time.perf_counter() - started) * 1000)}")
    print(f"event=save_corpus.load saves={len(paths)} failed={failed} days={days}")
    return 1 if failed or not paths else 0


class _Clock:
    now = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def load_db(src: Path, url: str, days: int = 30) -> int:
    """--load through the database (above); 1 if the check or any open fails."""
    logs.setup()
    migrate(url)
    rs = ruleset(load_opening(), load_renames(), "saves-forward", load_lock().release)
    database = open_database(url)
    clock, began, ids = _Clock(), datetime(2026, 1, 1, tzinfo=UTC), list[tuple[str, int, int]]()
    with database.engine.begin() as conn:
        account = accounts.create_account(conn, began)
        for path in sorted(src.glob("*.json")):
            text = path.read_text().strip()
            env = json.loads(text)
            t = int(env["save"]["time"])
            stored = rows.Written(state=text, format=int(env["format"]), rules_digest=str(env["rules"]), decisions=0,
                                  game_time=t, ended_at=None, build="before", release=0, camp_level=0)
            ids.append((path.name, rows.insert_save(conn, account, began, stored), t))
    checked = check(database.engine, rs)
    failed = checked.failed
    saves = PgSaves(database.engine, rs, clock)
    for name, save_id, t in ids:
        clock.now = began + timedelta(seconds=t + days * DAY_S)
        try:
            played, slices = saves.open(account, save_id).played, 1
            lines = len(played.lines)
            while played.catching_up_to is not None:   # a long absence comes back in slices, as the page asks
                played, slices = saves.advance(account, save_id), slices + 1
                lines += len(played.lines)
        except Exception as e:   # report every save, not only the first that fails
            failed += 1
            print(f"event=save_corpus.failed save={name} error={type(e).__name__}")
            continue
        print(f"event=save_corpus.opened save={name} time={played.save.time} lines={lines} slices={slices}")
    database.close()
    print(f"event=save_corpus.load saves={len(ids)} checked_failed={checked.failed} failed={failed} days={days}")
    return 1 if failed or not ids else 0


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        return write(Path(argv[0]))
    if len(argv) == 2 and argv[0] == "--load":
        url = os.environ.get("DATABASE_URL", "")
        return load_db(Path(argv[1]), url) if url else load(Path(argv[1]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
