"""The golden saves (tests/saves/golden/f<FORMAT>/): checkpoints of the scripted opening, each written as an encoded
text under this commit's rules, so a later format bump runs them through the upgrade chain (tests/saves/builds/test_golden.py).

    python tools/golden_saves.py <dir>    # write NN-seed-time.json, one encoded save each; run from app/
"""
import sys
from pathlib import Path

from ashfall_app.engine import Rules, Save, encode, new_save
from ashfall_app.rules.schema import load_opening, to_rules
from tests.rules.play.playthrough import Player

SEEDS = (0, 1, 2)
STOPS = (45, 120, 240, 400)
"""Game seconds a checkpoint is taken at (the opening's end follows them): story steps, the rack, the first mix,
orders and rests."""


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
    print(f"event=golden_saves.write saves={len(written)} dir={out}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        return write(Path(argv[0]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
