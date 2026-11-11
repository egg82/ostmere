"""Volume test v2: same arrivals, but coherent facts, only 1-2 per call, and a seeded lens per call."""
import json, random, subprocess, os, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEM = """You write one line for a town chronicle in a grim survival game: a valley where the sun stopped rising, survivors in a lamp-lit mining town.
Voice examples (from another game, for tone only):
- through the walls, shuffling noises can be heard.
- a bundle of sticks lies just beyond the threshold, wrapped in coarse furs.
- the shady builder has made off with your wood
- all residents in the hut perished in the fire.
Rules: lowercase. under 20 words. say what happened, not what it means. output only the line."""

# groups carry who could plausibly be missing, so facts cohere
GROUPS = [("a mother and two children", ["the father", "a third child", "nobody"]),
          ("an old man", ["his wife", "nobody"]), ("three miners", ["two of their crew", "nobody"]),
          ("a girl of about twelve", ["her parents", "her brother"]), ("a husband and wife", ["their son", "nobody"]),
          ("a priest", ["his flock", "nobody"]), ("two brothers", ["the third brother", "their father"]),
          ("a widow with a baby", ["her husband"]), ("a family of five", ["nobody", "the grandmother"]),
          ("a boy leading a blind man", ["the boy's mother"]), ("a woman alone", ["her husband", "her children"]),
          ("four people from the high farms", ["the rest of their farm"])]
CARRY = ["a cold lantern", "a sack of seed potatoes", "nothing", "a pickaxe", "a cage with a dead bird in it",
         "a family bible", "a goat", "a sword too big for them", "a cooking pot", "a bundle wrapped in a coat"]
DRAW = ["the fire", "the smell of bread", "the bell", "the lamps on the walls", "word of a guard on the gate"]
LENSES = ["tell it only through the one thing they carried.",
          "tell it as one thing one of them said, quoted, with nothing else.",
          "tell it as what one townsperson noticed about them.",
          "tell it as a plain record, like a ledger line.",
          "tell it as where they sat or slept that first night.",
          "tell it as what they asked for first."]

rng = random.Random(42)
def make(i):
    who, missing_opts = rng.choice(GROUPS)
    pool = {"missing": rng.choice(missing_opts), "carrying": rng.choice(CARRY), "drawn_by": rng.choice(DRAW)}
    keys = rng.sample(sorted(pool), rng.choice([1, 2]))
    facts = {"arrived": who, **{k: pool[k] for k in keys}}
    return i, facts, rng.choice(LENSES)

jobs = [make(i) for i in range(30)]

def run(job):
    i, facts, lens = job
    prompt = "Write the chronicle line for this arrival. " + lens + "\n" + json.dumps(facts)
    out = subprocess.run(["claude", "-p", "--setting-sources", "", "--model", "sonnet", "--no-session-persistence",
                          "--system-prompt", SYSTEM, prompt],
                         capture_output=True, text=True, timeout=300, cwd="/tmp")
    return {"i": i, "facts": facts, "lens": lens, "text": out.stdout.strip(), "err": out.stderr.strip()[:200], "rc": out.returncode}

with cf.ThreadPoolExecutor(max_workers=6) as ex:
    results = sorted(ex.map(run, jobs), key=lambda r: r["i"])
with open(os.path.join(HERE, "arrivals2.jsonl"), "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")
print("done", sum(1 for r in results if r["rc"] == 0 and r["text"]), "of", len(results))
for r in results:
    print(r["i"], r["text"] or r["err"])
