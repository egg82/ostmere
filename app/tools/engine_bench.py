"""Engine timing: reading every rich-run save, and the decisions route replaying the scripted opening player.

Run from app/: python -m tools.engine_bench [repeats] [--json]. Times each workload and `reference` `repeats` times,
interleaved so drift hits both, and prints every sample and the ratio of their minimums (CPU seconds, as the per-test
gate counts them); --json prints the samples as one JSON line instead, for tools/bench_ab.py, which is the gate (CI's
`engine-bench` job). The ratio to `reference` is only reported: it moves with the CPU type.
`reading` is test_cards_reading's read_everything over every rich save, summed; `steps` posts each of the scripted
player's decisions to /api/saves/{id}/decisions on a new save, the server's clock set to each decision's time, as the
page does (each one reads, advances, decides and writes the save). `steps` needs DATABASE_URL (a migrated database).
"""
import json
import logging
import os
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import psycopg
from fastapi.testclient import TestClient

from ashfall_app.api.convert import condition, mix, order_verb
from ashfall_app.engine import SaveMix, SetOrders, SetQueue, SwitchMix, TapCard, Verb
from ashfall_app.main import create_app
from tests.opening.playthrough import Player, opening_rules
sys.path.insert(0, str(Path(__file__).parent.parent / "tests" / "cards_contract"))  # the contract tests' own imports
from cards_world import rich_rules, rich_saves  # noqa: E402 -- sys.path is set on the line above
from test_cards_reading import read_everything  # noqa: E402 -- sys.path is set on the line above

Json = dict[str, Any]

def reference(n: int = 6_000_000) -> float:
    """CPU seconds of a fixed workload of the engine's own kind (dict and float churn), independent of the engine."""
    t0 = cpu_now()
    table: dict[int, float] = {}
    for i in range(n):
        table[i % 5003] = table.get(i % 5003, 0.0) * 0.5 + i * 1.25
    sorted(table.items(), key=lambda kv: -kv[1])
    return cpu_now() - t0


def cpu_now() -> float:
    return time.process_time()  # nanosecond clock; os.times() ticks at 10 ms, 2% of a sample


def decision(v: Verb) -> Json:
    """The wire form of a verb the scripted player makes."""
    match v:
        case TapCard():
            return {"kind": "tap_card", "card": v.card}
        case SwitchMix():
            return {"kind": "switch_mix", "mix_id": v.mix}
        case SaveMix():
            return {"kind": "save_mix", "mix": mix(v.mix).model_dump()}
        case SetOrders():
            return {"kind": "set_orders", "orders": [
                {"when": condition(o.when).model_dump(), "then": order_verb(o.then).model_dump()} for o in v.orders]}
        case SetQueue():
            return {"kind": "set_queue", "entries": [
                {"verb": order_verb(q.verb).model_dump(), "until": condition(q.until).model_dump()} for q in v.entries]}
        case _:
            raise ValueError(f"no wire form for {v}")


def reading() -> float:
    r = rich_rules()
    saves = rich_saves()
    t0 = cpu_now()
    for s in saves:
        read_everything(s, r)
    return cpu_now() - t0


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def steps(client: TestClient, clock: Clock, decisions: list[Json], ats: list[int], keep: bool = False) -> float:
    """CPU seconds to post every decision to a new save; the save is deleted after (an account holds five live saves
    and the account's only one cannot be, so the warm-up's `keep`s it)."""
    began = clock.now = clock.now + timedelta(days=1)
    made = client.post("/api/saves")
    assert made.status_code == 200, made.text
    save = made.json()["save"]["save_id"]
    t0 = cpu_now()
    for n, (at, d) in enumerate(zip(ats, decisions)):
        clock.now = began + timedelta(seconds=at)
        r = client.post(f"/api/saves/{save}/decisions", json={"decision": d, "after": n})
        assert r.status_code == 200, r.text
    took = cpu_now() - t0
    if not keep:
        gone = client.post(f"/api/saves/{save}/delete")
        assert gone.status_code == 200, gone.text
    return took


def interleaved(repeats: int, run: Callable[[], float]) -> tuple[list[float], list[float]]:
    """`repeats` samples of the reference and of `run`, alternating, so a slow stretch of the runner hits both."""
    refs: list[float] = []
    runs: list[float] = []
    for _ in range(repeats):
        refs.append(reference())
        runs.append(run())
    return refs, runs


def fmt(samples: list[float]) -> str:
    return ",".join(f"{s:.3f}" for s in samples)


def report(name: str, refs: list[float], runs: list[float]) -> None:
    """Print every sample and the minimums the ratio uses. Best-of-N is the estimator for how fast the code can run:
    noise only ever adds time."""
    ref, seconds = min(refs), min(runs)
    print(f"{name}={seconds:.3f}s reference={ref:.3f}s ratio={seconds / ref:.3f} n={len(runs)} "
          f"{name}_samples={fmt(runs)} reference_samples={fmt(refs)}")


def main(repeats: int, as_json: bool) -> int:
    logging.disable(logging.INFO)  # one request line per step would bury the results
    os.environ.setdefault("ASHFALL_RATE_KEY", "bench-rate-key")  # the app refuses to make an account without it
    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as db:
        db.execute("DELETE FROM tries")  # each process makes an account and saves; the limits count them for a day
        db.execute("DELETE FROM saves")  # the other tree's kept saves may be in a FORMAT this tree cannot read
    rules = opening_rules()
    p = Player(rules)
    p.play()
    decisions = [decision(v) for _, _, v in p.decisions]
    ats = [at for at, _, _ in p.decisions]
    found: dict[str, tuple[list[float], list[float]]] = {"reading": interleaved(repeats, reading)}
    clock = Clock()
    with TestClient(create_app(clock), base_url="https://bench", headers={"Origin": "https://bench"}) as client:
        steps(client, clock, decisions, ats, keep=True)  # warm the app and the rules caches
        found["steps"] = interleaved(repeats, lambda: steps(client, clock, decisions, ats))
    if as_json:
        print(json.dumps({n: {"reference": refs, "samples": runs} for n, (refs, runs) in found.items()}))
        return 0
    for n, (refs, runs) in found.items():
        report(n, refs, runs)
    return 0


if __name__ == "__main__":
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    sys.exit(main(int(nums[0]) if nums else 3, "--json" in sys.argv))
