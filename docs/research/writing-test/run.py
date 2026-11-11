"""Volume test: 30 stateless runtime-style calls, one arrival line each, seeded facts per call."""
import json, random, subprocess, os, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEM = """You write one line for a town chronicle in a grim survival game: a valley where the sun stopped rising, survivors in a lamp-lit mining town.
Voice examples (from another game, for tone only):
- through the walls, shuffling noises can be heard.
- a bundle of sticks lies just beyond the threshold, wrapped in coarse furs.
- all residents in the hut perished in the fire.
Rules: lowercase. one or two short sentences. say what happened, not what it means. output only the line."""

rng = random.Random(42)
WHO = ["a mother and two children", "an old man", "three miners", "a girl of about twelve", "a husband and wife",
       "a priest", "two brothers", "a widow with a baby", "a family of five", "a boy leading a blind man",
       "a woman alone", "four people from the high farms"]
MISSING = ["one child", "nobody", "the father", "a sister", "their eldest", "a husband", "nobody they will speak of",
           "two of the five who set out"]
CARRY = ["a cold lantern", "a sack of seed potatoes", "nothing", "a pickaxe", "a cage with a dead bird in it",
         "a family bible", "a goat", "a sword too big for them", "a cooking pot", "a bundle wrapped in a coat"]
DRAW = ["the fire", "the smell of bread", "the bell", "the lamps on the walls", "word of a guard on the gate"]
WEATHER = ["ash falling", "cold rain", "still air", "a wind off the pits", "frost"]

def call(i):
    facts = {"arrived": rng.choice(WHO), "missing": rng.choice(MISSING), "carrying": rng.choice(CARRY),
             "drawn_by": rng.choice(DRAW), "weather": rng.choice(WEATHER)}
    return i, facts

jobs = [call(i) for i in range(30)]

def run(job):
    i, facts = job
    prompt = "Write the chronicle line for this arrival.\n" + json.dumps(facts)
    out = subprocess.run(["claude", "-p", "--setting-sources", "", "--model", "sonnet", "--no-session-persistence",
                          "--system-prompt", SYSTEM, prompt],
                         capture_output=True, text=True, timeout=300, cwd="/tmp")
    return {"i": i, "facts": facts, "text": out.stdout.strip(), "err": out.stderr.strip()[:200], "rc": out.returncode}

with cf.ThreadPoolExecutor(max_workers=6) as ex:
    results = sorted(ex.map(run, jobs), key=lambda r: r["i"])
with open(os.path.join(HERE, "arrivals.jsonl"), "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")
print("done", sum(1 for r in results if r["rc"] == 0 and r["text"]), "of", len(results))
for r in results:
    print(r["i"], r["rc"], r["text"] or r["err"])
