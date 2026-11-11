"""A save's text with and without its manifest (db/manifests.py): stripping and putting back is exact on every golden
save of every format a rebase reads, and putting back leaves a whole text, or a text with no manifest given, alone;
leaving a given manifest out touches only a whole text carrying exactly that one."""
import json
from pathlib import Path

import pytest

from ashfall_app import engine as e
from ashfall_app.db.manifests import stripped, whole, without
from tests.shipped_ruleset import ShippedRuleset

GOLDEN = Path(__file__).resolve().parents[1] / "saves" / "golden"
TEXTS = sorted(p for f in range(e.OLDEST_FORMAT, e.FORMAT + 1) for p in (GOLDEN / f"f{f}").glob("*.json"))


def test_the_golden_saves_cover_every_format_a_rebase_reads():
    formats = {json.loads(p.read_text())["format"] for p in TEXTS}
    assert formats == set(range(e.OLDEST_FORMAT, e.FORMAT + 1))


@pytest.mark.parametrize("path", TEXTS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_a_stripped_text_put_back_is_the_text(path: Path):
    text = path.read_text().strip()
    bare, manifest = stripped(text)
    assert set(json.loads(bare)) == {"format", "rules", "save"}
    assert json.loads(manifest) == json.loads(text)["manifest"]
    assert len(bare) + len(manifest) < len(text)
    assert whole(bare, manifest) == text


def test_a_save_encoded_today_round_trips_through_its_stripped_form(shipped_ruleset: ShippedRuleset):
    rules = shipped_ruleset.rs.rules
    text = e.encode(e.new_save(rules), rules)
    assert whole(*stripped(text)) == text
    assert e.decode(whole(*stripped(text)), rules) == e.new_save(rules)


def test_a_whole_text_or_one_given_no_manifest_is_left_alone():
    text = TEXTS[-1].read_text().strip()
    bare, manifest = stripped(text)
    assert whole(text, manifest) == text
    assert whole(text, '{"other":1}') == text
    assert whole(bare, None) == bare
    assert whole("not a save", manifest) == "not a save"
    assert whole('{"format":10,"rules":"d","save":{}}', "{}") == '{"format":10,"manifest":{},"rules":"d","save":{}}'


@pytest.mark.parametrize("path", TEXTS, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_leaving_out_the_texts_own_manifest_is_stripping_it(path: Path):
    text = path.read_text().strip()
    bare, manifest = stripped(text)
    assert without(text, manifest) == bare
    assert without(text, manifest[:-1] + ',"x":1}') == text
    assert without(bare, manifest) == bare
    assert without("not a save", manifest) == "not a save"
