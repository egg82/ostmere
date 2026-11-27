"""`app/tools/gates.sh` runs every gate the "Structural gates" table in docs/engineering.md names, so a gate added to
the table without being added to the script fails here."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parents[2]
GATE_PATH = re.compile(r"`(app/[\w./-]+\.(?:py|mjs))`")


def table_gates() -> set[str]:
    text = (ROOT / "docs" / "engineering.md").read_text()
    section = text.split("## Structural gates", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in section.splitlines() if line.startswith("| `app/")]
    return {m.group(1) for row in rows if (m := GATE_PATH.search(row.split("|")[1]))}


def test_the_script_runs_every_gate_in_the_table():
    gates = table_gates()
    assert len(gates) >= 10, f"only {len(gates)} gate rows read from the table: the parse found nothing"
    script = (ROOT / "app" / "tools" / "gates.sh").read_text()
    missing = sorted(g for g in gates if not re.search(rf"(?<![\w/.-]){re.escape(g)}(?![\w/.-])", script))
    assert not missing, f"app/tools/gates.sh does not run: {missing}"
