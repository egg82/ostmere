"""Records fixtures/lump_saves_d3400d5.json: each scenario of lump_saves_world played to its SAVED_AT and encoded by
the engine of d3400d5, the last before lumps were paid by work. Run with that engine on the path, from app/:

    git archive d3400d5 app/ashfall_app | tar -x -C <dir>
    mkdir -p <dir>/app/tests/engine/fixtures && cp tests/engine/{lump_saves_world,record_lump_saves}.py <dir>/app/tests/engine/
    cd <dir>/app && PYTHONPATH=. python -m tests.engine.record_lump_saves

then copy the fixture back. Run from <dir>/app: from this checkout, the current directory would put this engine first.
"""
import json
from pathlib import Path

from ashfall_app.engine import advance, encode
from tests.engine.lump_saves_world import SAVED_AT, rules, started

if __name__ == "__main__":
    r = rules()
    found = {name: encode(advance(started(r, name), r, t), r) for name, t in SAVED_AT.items()}
    out = Path(__file__).parent / "fixtures" / "lump_saves_d3400d5.json"
    out.write_text(json.dumps(found, indent=1, sort_keys=True) + "\n")
    print("wrote", out)
