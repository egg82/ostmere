#!/usr/bin/env python3
"""Flag the flat-story shapes (docs/research/flat-story.md) in content/beats.yaml.

Usage: flatcheck.py [beats.yaml] [--route route.json] [--decisions decisions.jsonl] [--days day_one,...]
  --days: check only these day lists (default: every day_*: list). A promise only a left-out list opens may be
    advanced or paid by a spine beat unflagged.
  --route: JSON {"B1": day, ...} giving one simulated route's landing days; default is each beat's target_day.
    Optional keys for the in-day check: "hours" {"H1": h, ...} (game hours after the opening's end) and
    "visits" {"H1": "V1", ...}; defaults are each day entry's target_hour and visit.
Prints one line per flag, by beat id (week flags name the week and its beats), then accepted exceptions.
Exit status 1 if any flag is not accepted in decisions.jsonl ({"status": "accepted", "accepts": [{"beat", "flag"}]}).
The side_layer: list is checked on every run (kind, chapter, thread, offers; no turn; no spine or chapter gate names a side id).
Stdlib only: parses the flow-mapping subset of YAML that beats.yaml uses.

Every day_*: list is checked, each against its own <list>_near_promise. The day_one: list (H beats, one-off steps, P0's stages) is checked twice: its beats are spliced into the spine just
before the beat that closes the day (its last ref), so every spine check sees them; and the day's own order is checked
by the hour (gates land before what they gate, shape runs, the near promise touched on every visit).
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

STALE_DAYS = 14          # an open promise must be advanced or paid within this many days
UNMOVED_DAYS = 14        # a recurring character (3+ moves) must move again within this many days
RECURRING_MIN = 3
COUNTERS = {"skill_level", "arrivals", "journal_entries", "expeditions", "region_days"}
VALUES = {
    "turn": {"up", "down"},
    "outcome": {"yes", "yes_but", "no", "no_and"},
    "cost": {"none", "time", "people", "stores", "option", "trust"},
    "register": {"dread", "wry", "warm", "grim", "wonder"},
}
SIDE = {
    "kind": {"find", "trip", "arc", "comfort", "thread"},
    "offers": {"decision", "spend", "both"},
}
SIDE_FIELDS = {"id", "kind", "chapter", "thread", "offers", "gate"}
TOKEN = re.compile(r'\s*(?:([{}\[\],:])|"([^"]*)"|([^{}\[\],:"\s][^{}\[\],:]*))')


def scalar(v):
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return {"true": True, "false": False}.get(v, v)


def parse_flow(text):
    """Parse one YAML flow node (mapping, sequence or scalar)."""
    toks, pos = [], 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            if text[pos:].strip() == "":
                break
            raise ValueError("cannot parse near: %r" % text[pos:pos + 40])
        pos = m.end()
        if m.group(1):
            toks.append(("p", m.group(1)))
        elif m.group(2) is not None:
            toks.append(("s", m.group(2)))
        else:
            toks.append(("s", scalar(m.group(3).strip())))
    i = 0

    def node():
        nonlocal i
        kind, v = toks[i]
        i += 1
        if (kind, v) == ("p", "{"):
            d = {}
            while toks[i] != ("p", "}"):
                k = toks[i][1]
                assert toks[i + 1] == ("p", ":"), "expected ':' after %r" % k
                i += 2
                d[k] = node()
                if toks[i] == ("p", ","):
                    i += 1
            i += 1
            return d
        if (kind, v) == ("p", "["):
            out = []
            while toks[i] != ("p", "]"):
                out.append(node())
                if toks[i] == ("p", ","):
                    i += 1
            i += 1
            return out
        assert kind == "s", "unexpected %r" % (v,)
        return v

    result = node()
    assert i == len(toks), "trailing tokens"
    return result


def read_block(lines, key):
    """Items of a top-level block sequence of flow mappings, e.g. 'beats:'."""
    items, buf, inside = [], "", False
    for line in lines:
        bare = line.split(" #")[0].rstrip() if not line.lstrip().startswith("#") else ""
        if not inside:
            inside = bare == key + ":"
            continue
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        if not bare.strip():
            continue
        if bare.lstrip().startswith("- "):
            if buf:
                items.append(parse_flow(buf))
            buf = bare.lstrip()[2:]
        else:
            buf += " " + bare.strip()
    if buf:
        items.append(parse_flow(buf))
    return items


def read_scalar(lines, key):
    for line in lines:
        m = re.match(r"%s:\s*(\S+)\s*(?:#.*)?$" % re.escape(key), line)
        if m:
            return m.group(1)
    return None


def gate_leaves(g):
    if "all" in g:
        return [leaf for sub in g["all"] for leaf in gate_leaves(sub)]
    return [k for k in g]


def runs(flags, seq, key, n, kind, only=None):
    """Flag n or more beats in a row with the same value of key (only: count just these values)."""
    run = []
    for b in seq:
        v = b.get(key)
        if only and v is None:
            continue
        if run and v == run[-1].get(key) and (only is None or v in only):
            run.append(b)
        else:
            run = [b] if (only is None or v in only) else []
        if len(run) == n:
            flags.append((b["id"], kind, "%s %s in a row from %s" % (n, v, run[0]["id"])))
        elif len(run) > n:
            flags.append((b["id"], kind, "run of %s continues (%d)" % (v, len(run))))


def check(beats, regions, route, outside=frozenset()):
    """outside: promises a day list left out by --days opens; a spine beat may advance or pay one unflagged."""
    flags = []  # (beat_or_week, kind, detail)
    for b in beats:
        b["day"] = route.get(b["id"], b["target_day"])
    every = sorted(beats, key=lambda b: b["day"])  # stable: authored order breaks ties
    beats = [b for b in every if b.get("kind") != "offer"]   # offers carry a promise and a thread, not a turn
    last_region_day = max(r["open_day"] for r in regions)

    for b in beats:
        for f, ok in VALUES.items():
            if f in b and b[f] not in ok:
                flags.append((b["id"], "bad_value", "%s=%r" % (f, b[f])))
        if b.get("turn") in (None, "none"):
            flags.append((b["id"], "turn_none", "no turn declared"))
        if not b.get("moves"):
            flags.append((b["id"], "moves_none", "moves no one"))
        leaves = gate_leaves(b["gate"])
        if len(leaves) == 1 and leaves[0] in COUNTERS:
            flags.append((b["id"], "gate_single_counter", "gate is one %s" % leaves[0]))

    # runs: turn (3+), clean yes among attempted beats (2+), register (4+)
    runs(flags, beats, "turn", 3, "turn_run3")
    runs(flags, beats, "outcome", 2, "yes_run2", only={"yes"})
    runs(flags, beats, "register", 4, "register_run4")

    weeks = defaultdict(list)
    for b in beats:
        weeks[(b["day"] - 1) // 7 + 1].append(b)
    for w, bs in sorted(weeks.items()):
        label = "W%d(%s-%s)" % (w, bs[0]["id"], bs[-1]["id"])
        net = sum({"up": 1, "down": -1}.get(b.get("turn"), 0) for b in bs)
        if (w - 1) * 7 + 1 < last_region_day and net > 0:
            flags.append((label, "week_net_up", "net %+d before the last region" % net))
        if not any(b.get("outcome") in ("no", "no_and") for b in bs):
            flags.append((label, "week_no_failure", "no no/no_and"))
        costs = [b.get("cost") for b in bs if b.get("cost") not in (None, "none")]
        if not costs:
            flags.append((label, "week_no_cost", "every cost none"))
        elif len(set(costs)) == 1:
            flags.append((label, "week_one_cost_kind", "every cost is %s" % costs[0]))

    # promises
    opened, touched, paid = {}, {}, set()
    for b in every:
        for p in b.get("opens", []):
            opened[p] = touched[p] = b["day"]
        for key in ("advances", "pays"):
            for p in b.get(key, []):
                if (p not in opened or p in paid) and p not in outside:
                    flags.append((b["id"], "promise_unopened", "%s %s before it opens or after it is paid" % (key, p)))
                touched[p] = b["day"]
        for p in b.get("pays", []):
            paid.add(p)
        live = [p for p in opened if p not in paid]
        for p in live:
            if b["day"] - touched[p] > STALE_DAYS:
                flags.append((b["id"], "promise_stale", "%s untouched since day %d" % (p, touched[p])))
                touched[p] = b["day"]  # report each stale stretch once
        if not live and b is not beats[-1]:
            flags.append((b["id"], "promise_none_open", "nothing open after this beat"))
    for p in sorted(set(opened) - paid):
        flags.append((beats[-1]["id"], "promise_never_paid", p))

    # characters
    seen = defaultdict(list)
    for b in beats:
        for c in b.get("moves", []):
            seen[c].append(b)
    for c, bs in seen.items():
        if len(bs) < RECURRING_MIN:
            continue
        for a, z in zip(bs, bs[1:]):
            if z["day"] - a["day"] > UNMOVED_DAYS:
                flags.append((z["id"], "character_unmoved", "%s unmoved days %d-%d" % (c, a["day"], z["day"])))

    # threads
    threads = defaultdict(list)
    for b in every:
        t = b.get("thread")
        if not t:
            flags.append((b["id"], "thread_orphan", "no thread"))
            continue
        threads[t["id"]].append((b, t["at"]))
    for tid, items in threads.items():
        if len(items) < 2 or items[0][1] != "start":
            flags.append((items[0][0]["id"], "thread_orphan", "%s has %d beat(s), first is %s" % (tid, len(items), items[0][1])))
        if not any(at == "end" for _, at in items):
            flags.append((items[-1][0]["id"], "thread_no_end", tid))
    return flags


def splice_day(beats, day):
    """The spine with the day's beats placed just before the beat that closes the day (its last ref)."""
    refs = [e["id"] for e in day if e.get("kind") == "ref"]
    if not refs:
        return beats
    close = [i for i, b in enumerate(beats) if b["id"] == refs[-1]][0]
    extra, last_day = [], None
    for e in day:
        if e.get("kind") in ("beat", "offer"):
            extra.append(dict(e, target_day=e.get("target_day", last_day)))
        last_day = e.get("target_day", last_day)
    return beats[:close] + extra + beats[close:]


def gate_refs(g):
    """(mode, ids) pairs: 'all' means every id must land first, 'any' means at least one."""
    out = []
    if not isinstance(g, dict):
        return out
    for k, v in g.items():
        if k == "all":
            for sub in v:
                out += gate_refs(sub)
        elif k == "any":
            ids = [i for sub in v for _, ids in gate_refs(sub) for i in ids]
            out.append(("any", ids))
        elif k in ("beat", "project"):
            out.append(("all", [v]))
        elif k in ("hours_after", "days_after"):
            ref = v.get("beat") or v.get("project")
            if ref:
                out.append(("all", [ref]))
    return out


def day_close(story, refs):
    """The day's closing beat: its last ref when the day has a second one, else (a day whose only ref opens it) its
    last story entry when that is a chapter beat."""
    if len(refs) > 1:
        return refs[-1]
    return story[-1] if refs and story[-1].get("kind") == "beat" else None


def check_day(name, day, beats, known, near, hours, visits):
    """The in-day order: gates first, shape runs over the day's beats, the near promise on every visit."""
    flags = []
    by_id = {b["id"]: b for b in beats}
    items = []
    for e in day:
        it = dict(by_id[e["id"]], **e) if e.get("kind") == "ref" else dict(e)
        it["hour"] = hours.get(it["id"], it["target_hour"])
        it["visit"] = visits.get(it["id"], it.get("visit"))
        items.append(it)
    land = {it["id"]: it["hour"] for it in items}

    def landed(ref):
        if ref in land:
            return land[ref]
        stages = [h for i, h in land.items() if i.startswith(ref + ".")]
        return max(stages) if stages else None   # a project is done when its last stage is

    # gates land no later than what they gate; refs outside the day must be known ids landing before it
    for it in items:
        if it.get("kind") == "ref" and it is items[0]:
            continue   # the day's opening ref lands before the day starts
        for mode, refs in gate_refs(it.get("gate", {})):
            hs = [(r, landed(r)) for r in refs]
            for r, h in hs:
                if h is None and r not in known:
                    flags.append((it["id"], "day_gate_unknown", "gate names %s, not a known id" % r))
            inday = [(r, h) for r, h in hs if h is not None]
            late = [(r, h) for r, h in inday if h > it["hour"]]
            if mode == "all" and late:
                for r, h in late:
                    flags.append((it["id"], "day_gate_order", "lands at %sh before its gate %s (%sh)" % (it["hour"], r, h)))
            if mode == "any" and inday and len(late) == len(inday):
                flags.append((it["id"], "day_gate_order", "lands at %sh before any of %s" % (it["hour"], [r for r, _ in inday])))

    seq = sorted(items, key=lambda it: it["hour"])   # stable: authored order breaks ties
    story = [it for it in seq if it.get("kind") in ("beat", "ref")]
    refs = [it for it in items if it.get("kind") == "ref"]
    if refs and story[0]["id"] != refs[0]["id"]:
        flags.append((story[0]["id"], "day_order", "lands before the day's opening beat %s" % refs[0]["id"]))
    close = day_close(story, refs)
    if close and story[-1]["id"] != close["id"]:
        flags.append((story[-1]["id"], "day_order", "lands after the day's closing beat %s" % close["id"]))
    authored = [it["id"] for it in items if it.get("kind") in ("beat", "ref")]
    if [it["id"] for it in story] != authored:
        flags.append((name, "day_order", "route order %s differs from authored %s"
                      % ([it["id"] for it in story], authored)))
    for it in story:
        if it.get("kind") == "beat":
            missing = [f for f in ("turn", "cost", "moves", "thread", "register", "visit") if f not in it]
            if missing:
                flags.append((it["id"], "day_fields", "missing %s" % ", ".join(missing)))
    runs(flags, story, "turn", 3, "turn_run3")
    runs(flags, story, "outcome", 2, "yes_run2", only={"yes"})
    runs(flags, story, "register", 4, "register_run4")

    # the near promise: opened before it is touched, paid by the day's closing beat, touched on every visit
    if near:
        state = None
        touched = defaultdict(list)
        for it in story:
            for key in ("opens", "advances", "pays"):
                if near in it.get(key, []):
                    if (key == "opens") != (state is None) or state == "paid":
                        flags.append((it["id"], "near_order", "%s %s while it is %s" % (key, near, state or "unopened")))
                    state = {"opens": "open", "advances": "open", "pays": "paid"}[key]
                    touched[it["visit"]].append(it["id"])
        if close and near not in close.get("pays", []):
            flags.append((close["id"], "near_unpaid", "the day's closing beat does not pay %s" % near))
        day_visits = []
        for it in story:
            v = it["visit"]
            if v and v != refs[0].get("visit") and v not in day_visits:
                day_visits.append(v)
        for v in day_visits:
            if not touched.get(v):
                flags.append((v, "near_untouched", "no beat in %s opens, advances or pays %s" % (v, near)))
    return flags


def gate_scalars(g):
    """Every scalar a gate holds, at any depth: ids named as values or as the keys' arguments."""
    if isinstance(g, dict):
        return [x for v in g.values() for x in gate_scalars(v)]
    if isinstance(g, list):
        return [x for v in g for x in gate_scalars(v)]
    return [g]


def check_side(side, chapters, spine_entries):
    """The side layer's fields, no turn field on a side entry, and no spine or chapter gate naming a side id.
    chapters: {day list name: entries}; spine_entries: every spine and chapter entry (they carry the gates and threads)."""
    flags = []
    threads = {e["thread"]["id"] for e in spine_entries if isinstance(e.get("thread"), dict)}
    ids = [e.get("id") for e in side]
    for e in side:
        i = e.get("id")
        if ids.count(i) > 1:
            flags.append((i, "side_dup", "id appears %d times" % ids.count(i)))
        for f, ok in SIDE.items():
            if e.get(f) not in ok:
                flags.append((i, "side_" + f, "%s=%r" % (f, e.get(f))))
        if e.get("chapter") not in chapters:
            flags.append((i, "side_chapter", "chapter=%r" % (e.get("chapter"),)))
        if e.get("thread") not in threads:
            flags.append((i, "side_thread", "thread=%r" % (e.get("thread"),)))
        if "turn" in e:
            flags.append((i, "side_turn", "a side entry declares no turn"))
        for f in sorted(set(e) - SIDE_FIELDS - {"turn"}):
            flags.append((i, "side_field", "unknown field %s" % f))
    named = set(ids)
    for e in spine_entries:
        for x in sorted(named.intersection(gate_scalars(e.get("gate", {})))):
            flags.append((e["id"], "side_gated", "gate names side id %s" % x))
    return flags


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("beats", nargs="?", default=os.path.join(here, "..", "beats.yaml"))
    ap.add_argument("--route")
    ap.add_argument("--days", help="comma-separated day lists to check; default every day_*: list")
    ap.add_argument("--decisions", default=os.path.join(here, "..", "decisions.jsonl"))
    a = ap.parse_args()
    lines = open(a.beats).read().splitlines()
    beats, regions = read_block(lines, "beats"), read_block(lines, "regions")
    assert beats and regions, "no beats or regions parsed"
    day_names = [m.group(1) for m in (re.match(r"(day_\w+):\s*$", l) for l in lines) if m]
    only = a.days.split(",") if a.days else day_names
    days = {n: read_block(lines, n) for n in day_names if n in only}
    route = json.load(open(a.route)) if a.route else {}
    accepted = set()
    if os.path.exists(a.decisions):
        for line in open(a.decisions):
            if line.strip():
                d = json.loads(line)
                if d.get("status") == "accepted":
                    accepted |= {(x["beat"], x["flag"]) for x in d.get("accepts", [])}
    spine = beats
    for day in days.values():
        spine = splice_day(spine, day)
    outside = {p for n in day_names if n not in only for e in read_block(lines, n) for p in e.get("opens", [])}
    flags = check(spine, regions, route, frozenset(outside))
    side = read_block(lines, "side_layer")
    flags += check_side(side, {n: read_block(lines, n) for n in day_names},
                        [*beats, *(e for n in day_names for e in read_block(lines, n))])
    known = {b["id"] for b in beats} | {p["id"] for p in read_block(lines, "projects")}
    for name, day in days.items():
        flags += check_day(name, day, beats, known, read_scalar(lines, name + "_near_promise"),
                           route.get("hours", {}), route.get("visits", {}))
    open_flags = [f for f in flags if (f[0], f[1]) not in accepted]
    for f in open_flags:
        print("%-16s %-20s %s" % f)
    for f in flags:
        if (f[0], f[1]) in accepted:
            print("%-16s %-20s %s  [accepted]" % f)
    counts = Counter(f[1] for f in open_flags)
    print("beats=%d %s side=%d flags=%d accepted=%d %s" % (
        len(beats), " ".join("%s=%d" % (n, len(d)) for n, d in days.items()), len(side), len(open_flags), len(flags) - len(open_flags),
        " ".join("%s=%d" % kv for kv in sorted(counts.items()))))
    sys.exit(1 if open_flags else 0)


if __name__ == "__main__":
    main()
