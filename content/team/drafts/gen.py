"""Generate the lines-pass inputs for days four to six and B7, or with --week-two for week two's chapters.

Usage: python3 content/team/drafts/gen.py [--week-two] REPORT [chapter ...]
REPORT is the output of `python -m tests.weekone.report typical sharp babysitter whenever --lines` (week two:
`python -m tests.weektwo.report typical sharp babysitter whenever --lines`); no chapter means all of the week's.
Week two's chapter table is `week-two-chapters.toml` beside this file; week one's is below.
"""
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPEN = ROOT / "app/ashfall_app/opening"
TEAM = ROOT / "content/team"
UNW = "[day two: line to write]"
WEEK_TWO = "--week-two" in sys.argv
ARGS = [a for a in sys.argv[1:] if a != "--week-two"]
REPORT = Path(ARGS[0])
ONLY = ARGS[1:]
BRIEF_FILE = "week-two-lines-brief.md" if WEEK_TWO else "days-four-to-seven-lines-brief.md"
SPEC = "week-two.md" if WEEK_TWO else "days-four-to-seven.md"
BRIEF = (TEAM / BRIEF_FILE).read_text().splitlines()

CHAPTERS = {
    "day-four": dict(file="day_four", title="day four's lines (the fog, B6)", prev="day-three", sec=(67, 103)),
    "day-five": dict(file="day_five", title="day five's lines (the stone and the pair)", prev="day-four", sec=(104, 139)),
    "b7": dict(file="b7", title="B7's lines (the wolves at the edge of the light)", prev="day-five", sec=(140, 152)),
    "day-six": dict(file="day_six", title="day six's lines (keeping it, G2)", prev="b7", sec=(153, 182)),
}

# brief name -> toml key, where they differ
RENAMES = {
    "day-four": {"l_stack_1": "l_stack4_1", "l_stack_2": "l_stack4_2", "l_find_ashroot_bank": "l_find_for_11",
                 "l_find_pot_hook": "l_find_scav_19", "l_find_hoop": "l_find_scav_20", "l_find_dry_birch": "l_find_wc_20",
                 "l_find_thick_stew": "l_find_cook_6"},
    "day-five": {"l_find_dry_kindling": "l_arcana_5", "l_stones_3": "l_stones_done"},
    "b7": {"l_find_old_wolf": "l_melee_3"},
    "day-six": {"l_bedding_3": "l_bedding_done"},
}

# keys the lead adds to the toml's pool lists: each pool is asked for three lines (_1 is in the data file, _2 and _3 are not)
POOLS = [f"l_fight_{f}_{o}" for f in ("hunt", "rats", "crows") for o in ("won", "lost")]
EXTRA_KEYS = {"b7": [f"{p}_{n}" for p in POOLS for n in (2, 3)]}

H = {
    "day-four": ["l_fog_1", "l_sign_1", "l_sign_2", "l_stack4_1", "l_stack4_2", "l_b6_1", "l_b6_2", "l_b6_3"],
    "day-five": ["l_ridge_1", "l_ridge_2", "l_pair_1", "l_pair_2", "l_join2_1", "l_join2_2"],
    "b7": ["l_b7_1", "l_b7_2", "l_b7_3"],
    "day-six": ["l_hunt_1", "l_hunt_2", "l_g2_1", "l_g2_2", "l_g2_3"],
}

# extra brief paragraphs for the chapter, from "The Camp, finds and Arcana levels", with the toml's names
EXTRA = {
    "day-four": """### The Camp and finds (this chapter's)

**l_camp_11** (the stew holds 18). **l_find_for_11** (Foraging, an ashroot bank the fog kept soft), **l_find_scav_19**
(Scavenging, a pot hook and chain in the ditch by the track), **l_find_scav_20** (Scavenging, an iron hoop off a barrel,
half under the ash), **l_find_wc_20** (Woodcutting, a birch dead on its feet, dry right through), **l_find_cook_6**
(Cooking, a stew that keeps: the pot thicker by morning): one line each, by the mix, any visit; never wolves at the
camp's edge, never the stone's heat past what the player's hand does, nothing of week 2. The brief's names for these
were `l_find_ashroot_bank`, `l_find_pot_hook`, `l_find_hoop`, `l_find_dry_birch`, `l_find_thick_stew`.""",
    "day-five": """### Arcana levels (this chapter's)

**l_arcana_5** (Arcana 5, a find: the hand on the stone dries a little wood, +dry wood; the brief's `l_find_dry_kindling`),
**l_arcana_6** (Arcana 6, the level's speed-up: the smoking catches more). One line each, by the mix, any visit; never
wolves at the camp's edge, never the stone's heat past what the player's hand does, nothing of week 2.""",
    "b7": """### Finds (this chapter's)

**l_melee_3** (Melee 3, a find: a wolf dead in the thorn, older than the hunt's, a pelt off it; the brief's
`l_find_old_wolf`): one line, by the mix, any visit; nothing of week 2.

### Fights, pests and hurts (this chapter's; replaces the brief's "Fights, pests and hurts")

**l_hurt** (the hurt chip shows: the player is hurt), **l_healed** (it clears by itself), **l_poultice** (the first
poultice: a poultice of clay and roots). One line each, any visit.

**The fight pools.** Each fight has a pool of lines for one fight won and one lost; the page shows one line per fight,
the runner's lines drawn in a shuffled order (each once before any repeats), so any line may follow any other, the same
line may come twice in a day, and the number of fights before it is anyone's. Write **three lines per pool**, as `_1`,
`_2` and `_3` (the lead adds `_2` and `_3` to the data file's lists):
- **l_fight_hunt_won_1..3**, **l_fight_hunt_lost_1..3**: the hunt, one plain line each. A lost hunt leaves the player
  hurt; the line does not say so.
- **l_fight_rats_won_1..3**, **l_fight_rats_lost_1..3**: the rats at the roots; a lost one says only what is short
  ("the roots are fewer").
- **l_fight_crows_won_1..3**, **l_fight_crows_lost_1..3**: the crows at the rack; a lost one says only what is short.

A pool line is one fight, plain and short, never gory, never dwelling on how a beast dies; hunting and skinning are a way
of life. It carries no count, no "again", no "another", no "this time", no real-time word, and no name.""",
    "day-six": """### The Camp (this chapter's)

**l_camp_12** (the 900 000-item camp level, lifted by G2: smoked holds 36, was 27).""",
}

# the checks of "Two to check first"
CHECK_FIRST = {
    "day-five": "**o_pair** sits on screen across absences and neither answer may read as the right one.",
    "day-six": "**o_pelt** is a small thing asked by someone new, and \"keep it\" must read as an ordinary answer, not a refusal.",
}

if WEEK_TWO:
    _w2 = tomllib.loads((TEAM / "drafts/week-two-chapters.toml").read_text())["chapters"]
    CHAPTERS = {ch: dict(file=c["file"], title=c["title"], prev=c["prev"], sec=c["sections"]) for ch, c in _w2.items()}
    RENAMES = {ch: c.get("renames", {}) for ch, c in _w2.items()}
    EXTRA_KEYS = {}
    H = {ch: c["h"] for ch, c in _w2.items()}
    EXTRA = {ch: c["extra"].strip() for ch, c in _w2.items()}
    CHECK_FIRST = {}

NOTES = """## What the earlier passes taught (read before writing)

From day one's and day three's voice passes and the lead's picks. Each cost a line its place:

- **Do not lift the brief's fact phrases.** Every draft of day three copied the spec's words ("frost greys everything",
  "a stick at a time"); the facts are attributes, not wording. Say it your own way.
- **A line must be true in every state that fires it, and the state lists below are the typical route's.** Read the
  "fires with" column of the wiring table: lines that fire at the same moment cannot contradict each other (a fire "lit"
  in one line while the other fires before it is lit was false), and a line that fires on return cannot say "as the
  light goes" or "just now".
- **A failed-card line fails on whichever input is short.** The wiring table lists every input and requirement of the
  card; a line naming one store ("not enough wood") is false when another is short, and a card that fails on a night or a
  skill never fails on stuff. Say only what is true whichever is short; a card shared with another person's task gets
  no "you".
- **A stage line is one of a card's stages (1 of 3, ...): do not say "again", do not repeat the stage before, and do not
  open two stages the same way.** A stage that cannot be finished yet is not "finished": the last stage line is shown
  when its stage begins to dry or cure, not when it is done.
- **Do not repeat a word the neighbouring line uses at the same moment** ("keep", "quiet", "larder" back to back).
  Lines that fire in one visit sit next to each other on screen.
- **Do not carry a card's label or upside into its line.** You are not shown the labels; do not describe the effect
  ("a bigger batch", "faster", "more").
- **The two answers of a choice are mirrors.** Neither reads as right, neither is the one with the better line; give
  both the same frame and length.
- **Name a thing one way throughout** ("the walk" vs the card's "run the track" read as two things).
- **A person's name is a slot.** `{n2}` (the man who joined on day three), `{n3}` (the woman) and `{n4}` (the old man)
  are filled by the page with that person's name, lowercased inside a line. A line may say `{n2}`, `{n3}` or `{n4}` where
  the design below names that person, and only once that person has joined in every state the line shows in: `{n2}` from
  day four on, `{n3}` and `{n4}` only at or after l_join2_2 (the pair is "she" and "the old man" before it, and in any
  line that can show before the pair has joined). The wiring and states tables show when each line fires. Where a line is not sure to have the person joined, write "he", "the
  woman" or "the old man". Write the slot exactly (`{n2}`, no spaces, no other braces); never invent a name; Lucy stays
  the one name written out. The line-length limit counts a slot as the name it shows (about six letters), and a line
  holds no digit.
- **Hard limit: no line is over 75 characters** (`app/tests/opening/test_line_length.py`, applied to every `l_` line;
  a line over fails CI and goes back). The set's median should stay at 45 or under. Count characters before sending;
  most lines should be well under.
- **Voice notes (day one's pass):** a line that echoes its own level label or another line shown in the same instant is
  changed first; "again" is a must-not even as "half as much again"; the stomach is not the stores."""


def brief_lines(a: int, b: int) -> str:
    return "\n".join(BRIEF[a - 1:b]).rstrip()


def heading_section(prefix: str) -> str:
    """The brief's section whose heading starts with `prefix`, up to the next heading of its level or above."""
    start = next(i for i, ln in enumerate(BRIEF) if ln.startswith(prefix))
    level = len(BRIEF[start]) - len(BRIEF[start].lstrip("#"))
    end = next((i for i in range(start + 1, len(BRIEF)) if re.match(rf"^#{{1,{level}}} ", BRIEF[i])), len(BRIEF))
    return "\n".join(BRIEF[start:end]).rstrip()


def chapter_section(sec) -> str:
    """A chapter's part of the brief: line numbers (week one) or heading prefixes (week two)."""
    return brief_lines(*sec) if isinstance(sec, tuple) else "\n\n".join(heading_section(h) for h in sec)


def notes_block() -> str:
    if not WEEK_TWO:
        return NOTES
    a, b = NOTES.index("- **A person's name is a slot."), NOTES.index("- **Hard limit")
    return NOTES[:a] + NOTES[b:]


def lenses() -> list[tuple[str, str]]:
    return [(m[1], m[2]) for m in (re.match(r"^\| (writer-\d) \| (.+) \|$", ln) for ln in BRIEF) if m]


def rules_block() -> str:
    text = heading_section("## Rules for every line")
    text = text.replace("- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter.",
                        "- **Length:** median 45 characters or fewer, 90th percentile 75 or fewer, per chapter; no line over 75.")
    folds = " A long absence folds into one count line (pools, below)." if WEEK_TWO else \
        " A long absence folds into one count line (`fight_*` pools, below)."
    for a, b in ((folds, " The page writes a long absence's count line; write the pools below."),):
        assert text.count(a) == 1, a
        text = text.replace(a, b)
    return text


def exemplars() -> str:
    d2 = (TEAM / "day-two-lines-brief.md").read_text().splitlines()
    table = "\n".join(d2[49:82])
    if WEEK_TWO:
        return f"## Voice exemplars (shipped, verbatim)\n\nRead them for voice; reuse no phrase from them.\n\n{table}"
    d3 = tomllib.loads((OPEN / "day_three.toml").read_text())["text"]
    rows = "\n".join(f"| {k} | {v} |" for k, v in d3.items() if k.startswith("l_") and UNW not in v)
    return (f"## Voice exemplars (shipped, verbatim)\n\nRead them for voice; reuse no phrase from them.\n\n{table}\n\n"
            f"Day three, which day four follows directly (every shipped line of it):\n\n| Key | Line |\n|---|---|\n{rows}")


def lens_table() -> str:
    rows = "\n".join(f"| {w} | {l} |" for w, l in lenses())
    return (f"## Lenses\n\n| Writer | Lens |\n|---|---|\n{rows}\n\nA lens is a way into the line, not a topic; "
            "a line that cannot take it plainly ignores it.")


# ---------- toml wiring ----------

def cond(c: dict) -> str:
    if c.get("test") == "at_most":
        return "not " + cond({**c, "test": "at_least"})
    if c.get("test") == "after_time":
        return f"the clock reaches {c['value'] / 3600:g} h"
    kind = c.get("subject_kind")
    if kind == "unlocked":
        return f"{c.get('unlock_kind')} {c.get('id')} unlocked"
    if kind == "card_count":
        return f"card {c['id']} done >= {c['value']}"
    return f"{kind} {c.get('id')} >= {c.get('value')}" if "value" in c else str(c)


def conds(cs) -> str:
    if cs is None:
        return ""
    cs = cs if isinstance(cs, list) else [cs]
    return "; ".join(cond(c) for c in cs)


def inputs(i) -> str:
    return ", ".join(f"{x['store']} x{x['items']}" for x in i)


def keys_in(o) -> list[str]:
    return o.get("line_keys", []) if isinstance(o, dict) else []


def wiring(data: dict, key: str) -> list[str]:
    out: list[str] = []
    for t in data.get("triggers", []):
        o = t.get("outcome", {})
        if key in keys_in(o):
            others = [k for k in keys_in(o) if k != key]
            out.append(f"trigger {t['id']} when {conds(t.get('when'))}" + (f"; requires {conds(t['requires'])}" if t.get("requires") else "")
                       + (f"; fires with {', '.join(others)}" if others else ""))
    for c in data.get("cards", []) + data.get("town_cards", []):
        fin = c.get("finished", {})
        if c.get("failed_line_key") == key:
            out.append(f"failed-card line of card {c['id']} ({c.get('presentation')}; lane {c.get('lane') or c.get('lanes', '-')}); inputs {inputs(c.get('inputs', [])) or 'none'}"
                       + (f"; requires {conds(c['requires'])}" if c.get("requires") else ""))
        for src, lk in (("cap", c.get("line_keys", [])), ("finished", keys_in(fin)), ("outcome", keys_in(c.get("outcome", {})))):
            if key in lk:
                pos = f"stage line {lk.index(key) + 1} of {len(lk)}" if src == "cap" else "line on finishing"
                out.append(f"{pos} of card {c['id']}" + (f" ({c.get('presentation')}; inputs {inputs(c.get('inputs', []))})" if src == "cap" else ""))
    for o in data.get("offers", []):
        if key in o.get("line_keys", []):
            out.append(f"offer {o['id']} line (on screen until answered; fires with {', '.join(k for k in o['line_keys'] if k != key) or 'nothing'})")
        for a in o.get("answers", []):
            if key in keys_in(a.get("outcome", {})):
                out.append(f"answer {a['id']} of offer {o['id']}: line when that answer is given")
    for c in data.get("cards", []) + data.get("standing", []):
        f = c.get("fight") or {}
        for lk, what in (("won_line_keys", "won"), ("lost_line_keys", "lost")):
            if key in f.get(lk, []):
                out.append(f"pool of lines for one fight {what}, of {c['id']} (side {f.get('side')} against {f.get('threat')}); "
                           f"one line per fight, drawn in a per-runner shuffle bag, so any line may follow any other and any count of fights has come before")
    for ch in data.get("chips", []):
        if key == ch.get("on_line_key"):
            out.append(f"chip {ch['id']} line when it shows")
        if key == ch.get("off_line_key"):
            out.append(f"chip {ch['id']} line when it clears (by a cure, or by itself where it has none)")
    for lv in data.get("camp_levels", []):
        if key in lv.get("line_keys", []):
            out.append(f"camp level at {lv['at_items']} items")
    for f in data.get("features", []):
        if key in str(f):
            out.append(f"feature {f['id']}")
    for s in data.get("standing", []):
        pass
    return out or ["(no wiring found)"]


def classify(k: str) -> str:
    if k.startswith("l_"):
        return "fail" if (k.endswith("_fail") or k.endswith("_dry")) else "line"
    for p, n in (("c_", "card label"), ("up_", "upside label"), ("store_", "store label"), ("action_", "action label"),
                 ("lane_", "lane label"), ("o_", "offer label"), ("a_", "offer answer label"), ("aim_", "aim label"),
                 ("pays_", "pays label"), ("camp_pays", "camp label"), ("chip_", "chip label"), ("skill_", "skill label"), ("n_", "journal note"),
                 ("dayend", "end card"), ("side_", "fight label"), ("threat_", "fight label")):
        if k.startswith(p):
            return n
    return "label"


# ---------- states ----------

def parse_report(path: Path) -> dict[str, dict[str, dict[str, list[str]]]]:
    """file -> key -> route -> [state strings]"""
    out: dict = {}
    f = k = None
    for ln in path.read_text().splitlines():
        if ln.startswith("== "):
            f = ln[3:].strip()
            out[f] = {}
        elif f and re.match(r"^  [a-z_0-9]+:", ln):
            k = ln.strip().split(":")[0]
            out[f][k] = {}
        elif ln.startswith("      ") and k:
            route, rest = ln.strip().split(" ", 1)
            out[f][k].setdefault(route, []).append(rest)
    return out


PAT = re.compile(r"V(\d+) (on return|present) \| (\d+) capped done \| answers (\[.*?\]) \| (.*?) \| queue (\d+)")


def summarize_key(by: dict[str, list[str]]) -> str:
    """One cell: where each route showed it (visit and present/on return), then the ranges across routes."""
    per, capped, ans, held, queue = [], [], set(), set(), []
    for route, states in by.items():
        ms = [m for m in map(PAT.match, states) if m]
        if not ms:
            per.append(f"{route} after the last visit")
            continue
        seen = sorted({(int(m[1]), m[2]) for m in ms})
        per.append(f"{route} " + ", ".join(f"V{v} {w}" for v, w in seen))
        for m in ms:
            capped.append(int(m[3])); ans |= set(eval(m[4])); held.add(m[5]); queue.append(int(m[6]))
    rng = lambda xs: f"{min(xs)}-{max(xs)}" if xs else "-"
    return (f"{'; '.join(per)} | capped done {rng(capped)} | answers so far, any of {sorted(ans)} | "
            f"{' / '.join(sorted(held))} | queue {rng(queue)}")


def states_table(file: str, keys: list[str], rep) -> str:
    rows = ["| key | where it showed (route, visit, present or on return) | state |", "|---|---|---|"]
    for k in keys:
        by = rep.get(k, {})
        if not by:
            rows.append(f"| {k} | never shown on any simulated route (design expectation in the brief applies) | |")
        else:
            cell = summarize_key(by).replace(" | ", "; ").split("; ", 1)
            rows.append(f"| {k} | {cell[0]} | {cell[1]} |")
    return "\n".join(rows)


def main() -> None:
    rep_all = parse_report(REPORT)
    for ch, cfg in CHAPTERS.items():
        if ONLY and ch not in ONLY:
            continue
        data = tomllib.loads((OPEN / f"{cfg['file']}.toml").read_text())
        text = data["text"]
        unw = [k for k, v in text.items() if v == UNW]
        lkeys = [k for k in unw if k.startswith("l_")]
        extra = EXTRA_KEYS.get(ch, [])
        pool1 = {k: k.rsplit('_', 1)[0] + '_1' for k in extra}
        rep = rep_all[f"{cfg['file']}.toml"]
        ren = {v: k for k, v in RENAMES[ch].items()}
        h = H[ch]
        assert all(k in unw for k in h), (ch, [k for k in h if k not in unw])
        out = TEAM / "drafts" / ch
        out.mkdir(parents=True, exist_ok=True)

        # per-key wiring for keys the brief does not spell out in a chapter section
        sect = chapter_section(cfg["sec"]) + "\n" + EXTRA[ch]
        covered = set(re.findall(r"l_\w+", sect))
        for m in re.finditer(r"(l_\w+?)_(\d)(?: to |\.\.)(?:l_\w+?_)?(\d)", sect):
            covered |= {f"{m[1]}_{i}" for i in range(int(m[2]), int(m[3]) + 1)}
        covered |= set(RENAMES[ch].values())
        unspelled = [k for k in lkeys if k not in covered]
        alll = lkeys + extra
        wire = ["| key | where it plays (from the data file) |", "|---|---|"]
        for k in alll:
            wire.append(f"| {k} | " + " / ".join(wiring(data, pool1.get(k, k))) + (" (a later entry of the pool: same wiring as its _1)" if k in pool1 else "") + " |")
        srep = {**rep, **{k: rep.get(pool1[k], {}) for k in extra}}

        body = f"""# {ch.replace('-', ' ').capitalize()}'s lines: the writers' brief

Spoilers: under `content/`, never shown to the owner. The spec is `{SPEC}`; the data is
`app/ashfall_app/opening/{cfg['file']}.toml`, where every key below reads "[day two: line to write]" (the marker's spelling is
the data file's; ignore it). The brief's design states are an expectation; the generated states below replace them.

## How the lines get written

Three blind proposers (Sonnet), one lens each (below), every key plus one alternate per key marked H; a critic scores the
drafts blind on `rubric.md` plus *true in every listed state?*; the lead picks line by line; code checks length, the
must-nots as a scan, and three-word echoes against content prose and every shipped line before them; a fresh agent's
voice pass reads every picked line and label in player order and writes the labels.

Each proposer's input is this file, its lens, and nothing else from `content/`. Facts are given as attributes, not
phrases.

{rules_block()}

{notes_block()}

{exemplars()}

{lens_table()}

## The lines

Each entry: the moment, the beat or side beat, the facts as attributes, the expected states, and anything special.
Keys named in the entries below that the data file spells differently are listed under "Brief names" at the end.

{chapter_section(cfg['sec'])}

{EXTRA[ch]}
"""
        if ch in CHECK_FIRST:
            body += f"\nTo check first: {CHECK_FIRST[ch]}\n"
        if ch == "day-six":
            body += "\nThe spear line (`l_spear`) is the one place a line may put the shaft and the scrap together.\n"
        body += f"""
## Where each key plays (read from the data file; "fires with" lines share one moment on screen)

{chr(10).join(wire)}

## Generated states (the simulator's `--lines` over the typical, sharp, babysitter and whenever routes; replaces the brief's expected states where they differ)

Visit numbers count from the first visit of the chapter's pass, per route (a find can fire in a later chapter's visits). 'present' = the player is there when it happens; 'on return' = reads it after an absence. A line must read right in every listed combination. The answers listed are everything answered so far in the whole week, not only this chapter's.

{states_table(cfg['file'], alll, srep)}
"""
        if ren:
            body += "\n## Brief names\n\nThe design briefs name these keys differently; this file's keys are the data file's:\n\n" + \
                "\n".join(f"- `{b}` is `{t}`" for t, b in ren.items()) + "\n"
        if unspelled:
            body += f"\n## Keys the brief does not spell out\n\nNo beat facts: write from the wiring table. Failed-card lines (`*_fail`, `*_dry`): what the card shows when tapped with the cost short; the player's try (or the person's), short of the means; one short line; no number. Stage lines: the card's stages in order, same register as the shipped stage lines of day two and three.\n\nKeys: {', '.join(unspelled)}\n"
        body += f"""
## Output

A TOML file, `key = "line"` per key below, in this order, lowercase, plain. Keys marked H also get `key_alt = "line"` right after. A draft missing an alternate is sent back. Every line within 75 characters; no digit; a name slot only as the rule above allows.

Keys ({len(alll)}, in order): {', '.join(alll)}

H keys (alt required): {', '.join(h)}
"""
        prevblock = ""
        if WEEK_TWO or cfg["prev"] != "day-three":
            prevblock = (f"\n## Shipped lines of the chapter before ({cfg['prev']})\n\n{{{{PREVIOUS_PICKS}}}}\n\n"
                         "(The lead fills this with the previous chapter's shipped lines before the proposers start; reuse no phrase from them.)\n")
        for i, (w, lens) in enumerate(lenses(), 1):
            head = (f"# Proposer {w} input: {cfg['title']}\n\nYou are writing {cfg['title'].split(' (')[0]}. This file is all you may see from the "
                    f"project's content; read nothing else.\n\n## Your lens\n\n{lens}\n\nA lens is a way into the line, not a topic; a line that "
                    f"cannot take it plainly ignores it.\n\n---\n\n")
            (out / f"proposer-{i}-input.md").write_text(head + body + prevblock)

        crit = (TEAM / "drafts/day-three/critic-input.template.md").read_text()
        rub = crit.split("## Rubric (verbatim)\n\n", 1)[1].split("\n---\n", 1)[0]
        ctext = (f"# Critic input (template): {cfg['title']}\n\nFill the three DRAFT blocks with the proposers' TOML, labelled A/B/C in shuffled order; "
                 "do not say which lens wrote which.\n\nYou score the three drafts blind on the rubric below, plus one row: *true in every listed state?* "
                 "(quote the state a line breaks). Check each line against the brief's rules and must-nots, and the 75-character limit. Score per key per draft; "
                 "name the best of the three per key and why in a clause.\n\n## Rubric (verbatim)\n\n" + rub + "\n---\n\n# The brief (verbatim)\n\n" + body + prevblock
                 + "\n\n## Drafts\n\n### Draft A\n\n{{DRAFT_A}}\n\n### Draft B\n\n{{DRAFT_B}}\n\n### Draft C\n\n{{DRAFT_C}}\n")
        (out / "critic-input.template.md").write_text(ctext)

        # manifest
        rows = [f"# {ch.capitalize()} keys manifest: every key in {cfg['file']}.toml still at the UNWRITTEN marker, in file order.",
                "# kind: line (a proposer writes it) | fail (failed-card line, a proposer writes it) | label (the voice pass writes it)"
                + (" | journal note (its own batch, after this one)." if WEEK_TWO else "."),
                "# limit: lines share a set limit: median <= 45 chars, p90 <= 75 across the chapter's l_ keys, and no line over 75 (app/tests/opening/test_line_length.py). Labels: none set.",
                "# alt: H = a proposer also writes key_alt. brief: the design brief's name where it differs (-: same).",
                f"# keys: {len(unw) + len(extra)}" + (f" ({len(extra)} of them are pool entries not yet in the data file; the lead adds them)" if extra else ""),
                "key\tkind\tlimit\talt\tbrief"]
        for k in unw:
            kind = classify(k)
            lim = "line<=75; set median<=45,p90<=75" if k.startswith("l_") else "n/a"
            rows.append(f"{k}\t{kind}\t{lim}\t{'H' if k in h else '-'}\t{ren.get(k, '-')}")
        for k in extra:
            rows.append(f"{k}\tline\tline<=75; set median<=45,p90<=75\t-\tnew pool entry")
        (out / "keys-manifest.tsv").write_text("\n".join(rows) + "\n")
        print(ch, "keys", len(unw), "lines", len(lkeys), "unspelled", len(unspelled), "never", sum(1 for k in lkeys if not rep.get(k)))


main()
