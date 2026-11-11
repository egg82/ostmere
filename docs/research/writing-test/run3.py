"""Volume test v3 + model golf: facts as attributes, big pools drawn without repeats, the implied-turn rule,
and the same 30 jobs run on haiku, sonnet and opus."""
import json, random, subprocess, os, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEM = """You write one line for a town chronicle in a grim survival game: a valley where the sun stopped rising, survivors in a lamp-lit mining town kept alive by its furnaces.
Voice examples (from another game, for tone only):
- through the walls, shuffling noises can be heard.
- a bundle of sticks lies just beyond the threshold, wrapped in coarse furs.
- the shady builder has made off with your wood
- all residents in the hut perished in the fire.
Rules: lowercase. under 25 words. say what happened, not what it means. never state the feeling or the moral. the facts are notes for you, not wording: put them in your own words, and leave out any that don't serve the line. output only the line."""

# who arrived: (people, who is absent and how) -- coherent by construction
GROUPS = [
    ({"adults": 2, "children": 0}, {"who": "son", "fate": "died on the road"}),
    ({"adults": 1, "children": 2, "adult": "mother"}, {"who": "father", "fate": "unknown"}),
    ({"adults": 1, "age": "old", "sex": "man"}, {"who": "wife", "fate": "buried before they left"}),
    ({"adults": 3, "trade": "miners"}, {"who": "two of the crew", "fate": "cave-in"}),
    ({"children": 1, "age": 12, "sex": "girl"}, {"who": "parents", "fate": "unknown"}),
    ({"adults": 1, "trade": "priest"}, {"who": "his congregation", "fate": "stayed behind"}),
    ({"adults": 2, "relation": "brothers"}, {"who": "third brother", "fate": "turned back"}),
    ({"adults": 1, "sex": "woman", "with": "infant"}, {"who": "husband", "fate": "died of fever"}),
    ({"adults": 2, "children": 3}, None),
    ({"children": 1, "sex": "boy", "with": "blind man, not his father"}, {"who": "boy's mother", "fate": "unknown"}),
    ({"adults": 4, "from": "the high farms"}, {"who": "the rest of the farm", "fate": "stayed"}),
    ({"adults": 1, "sex": "woman"}, {"who": "her children", "fate": "taken by something in the dark"}),
    ({"adults": 1, "trade": "smith", "injury": "burned hands"}, None),
    ({"adults": 2, "relation": "sisters", "age": "teens"}, {"who": "grandmother", "fate": "died two days back"}),
    ({"adults": 1, "trade": "deserter soldier"}, {"who": "his unit", "fate": "he won't say"}),
    ({"adults": 2, "relation": "old couple"}, None),
    ({"children": 2, "relation": "twins", "age": 7}, {"who": "everyone", "fate": "unknown"}),
    ({"adults": 1, "trade": "lamplighter from another town"}, {"who": "his town", "fate": "went dark"}),
    ({"adults": 3, "relation": "a family, one adult missing an arm"}, None),
    ({"adults": 1, "sex": "man", "state": "won't speak"}, {"who": "unknown", "fate": "unknown"}),
    ({"adults": 2, "trade": "peddlers"}, {"who": "their mule", "fate": "eaten"}),
    ({"adults": 1, "sex": "woman", "state": "heavily pregnant"}, {"who": "husband", "fate": "went back for supplies"}),
    ({"adults": 5, "trade": "quarry workers"}, None),
    ({"adults": 1, "trade": "schoolteacher", "with": "four pupils"}, {"who": "the other pupils", "fate": "parents came for them"}),
    ({"adults": 1, "age": "old", "sex": "woman"}, {"who": "everyone she knew", "fate": "outlived them"}),
    ({"adults": 2, "relation": "father and grown son"}, {"who": "mother", "fate": "fell on the pass"}),
    ({"adults": 1, "trade": "midwife"}, None),
    ({"children": 1, "sex": "boy", "age": 9}, {"who": "older sister", "fate": "sent him ahead"}),
    ({"adults": 2, "relation": "husband and wife", "state": "barely speaking"}, {"who": "daughter", "fate": "unknown"}),
    ({"adults": 1, "trade": "gravedigger"}, None),
]
ITEMS = [
    {"thing": "cap", "of": "wool", "size": "a child's"}, {"thing": "rag doll", "state": "one button eye"},
    {"thing": "seed potatoes", "amount": "a sack"}, {"thing": "pickaxe"}, {"thing": "birdcage", "state": "empty, door open"},
    {"thing": "family bible", "state": "names inked in the front, recent ones blotted"}, {"thing": "goat", "state": "thin"},
    {"thing": "sword", "fit": "too big for the carrier"}, {"thing": "cooking pot"}, {"thing": "lantern", "state": "no flame"},
    {"thing": "wedding ring", "worn": "on a string"}, {"thing": "letter", "state": "sealed, unaddressed"},
    {"thing": "hand bell"}, {"thing": "clock", "state": "stopped"}, {"thing": "spade"}, {"thing": "fiddle", "strings": 2},
    {"thing": "boots", "size": "a child's", "worn": "around the neck"}, {"thing": "dog", "state": "lame"},
    {"thing": "salt", "amount": "a twist of paper"}, {"thing": "door key", "to": "a house that burned"},
    {"thing": "hen", "state": "laying"}, {"thing": "candles", "amount": "a bundle"}, {"thing": "map", "state": "half burned"},
    {"thing": "knitting", "state": "unfinished, child-sized"}, {"thing": "flour", "amount": "half a sack"},
    {"thing": "portrait", "state": "face scratched out"}, {"thing": "medicine", "state": "nearly empty bottle"},
    {"thing": "hammer and tongs"}, {"thing": "whistle", "on": "a cord"}, {"thing": "nothing"},
]
LURES = ["the fire", "bread baking", "the bell", "the lamps on the walls", "a rumour there were guards", "smoke",
         "the furnace glow on the clouds", "a child who'd been sent ahead", "the sound of hammering", "they didn't choose; the road ended here"]
PLAIN = ["tell it as a plain record, like a ledger line. no turn at the end.",
         "tell it as a plain note of what happened, the way a watchman would log it."]
TURNED = ["tell it only through the one thing they carried.",
          "tell it as one thing one of them said, quoted, with nothing else.",
          "tell it as what one townsperson noticed about them.",
          "tell it as where they sat or slept that first night.",
          "tell it as what they asked for first."]
TURN_RULE = " end on a turn the reader completes: imply it, never state it, nothing overwrought."

def bag(rng, xs):
    """Shuffle bag: every item once before any repeats."""
    while True:
        ys = list(xs); rng.shuffle(ys)
        yield from ys

rng = random.Random(1011)
groups, items, lures = bag(rng, GROUPS), bag(rng, ITEMS), bag(rng, LURES)

def make(i):
    people, absent = next(groups)
    facts = {"people": people}
    extra = {"absent": absent, "item": next(items), "came for": next(lures)}
    if absent is None:
        del extra["absent"]
    for k in rng.sample(sorted(extra), rng.choice([1, 2])):
        facts[k] = extra[k]
    if rng.random() < 0.3:
        lens = rng.choice(PLAIN)
    else:
        lens = rng.choice(TURNED) + TURN_RULE
    return i, facts, lens

jobs = [make(i) for i in range(30)]
MODELS = ["haiku", "sonnet", "opus"]

def run(arg):
    model, (i, facts, lens) = arg
    prompt = "Write the chronicle line for this arrival. " + lens + "\n" + json.dumps(facts)
    out = subprocess.run(["claude", "-p", "--setting-sources", "", "--model", model, "--no-session-persistence",
                          "--system-prompt", SYSTEM, prompt],
                         capture_output=True, text=True, timeout=300, cwd="/tmp")
    return {"model": model, "i": i, "facts": facts, "lens": lens, "text": out.stdout.strip(),
            "err": out.stderr.strip()[:200], "rc": out.returncode}

with cf.ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(run, [(m, j) for m in MODELS for j in jobs]))
with open(os.path.join(HERE, "arrivals3.jsonl"), "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")
for m in MODELS:
    ok = [r for r in results if r["model"] == m and r["rc"] == 0 and r["text"]]
    print(m, "ok", len(ok), "of 30")
