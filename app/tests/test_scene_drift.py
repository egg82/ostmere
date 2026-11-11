"""tools/scene/drift.py reports served scene art that was built from other code than the checkout's, and the generator
stamps the digest it compares. Each case reads a manifest file by URL, as the CI job reads the live one."""
import json
import shutil
import sys
from pathlib import Path

import pytest

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import drift   # tools/scene, on the path from the line above


def manifest_at(tmp_path: Path, body: dict[str, object] | str) -> str:
    f = tmp_path / "manifest.json"
    f.write_text(body if isinstance(body, str) else json.dumps(body))
    return f.as_uri()


def test_a_manifest_stamped_with_the_checkouts_digest_matches(tmp_path: Path):
    code, line = drift.check(manifest_at(tmp_path, {"layers": [], "source": drift.source_digest()}))
    assert (code, "matches" in line) == (drift.MATCH, True)


def test_a_manifest_stamped_with_another_digest_is_reported(tmp_path: Path):
    code, line = drift.check(manifest_at(tmp_path, {"layers": [], "source": "0" * 16}))
    assert code == drift.DRIFT and "stale" in line


def test_a_manifest_with_no_digest_is_reported(tmp_path: Path):
    code, line = drift.check(manifest_at(tmp_path, {"layers": []}))
    assert code == drift.DRIFT and "no source digest" in line


@pytest.mark.parametrize("body", ["not json", "[1, 2]"])
def test_an_unreadable_manifest_is_unknown_not_a_match_or_drift(tmp_path: Path, body: str):
    assert drift.check(manifest_at(tmp_path, body))[0] == drift.UNREADABLE


def test_a_missing_manifest_is_unknown(tmp_path: Path):
    assert drift.check((tmp_path / "absent.json").as_uri())[0] == drift.UNREADABLE


def test_the_digest_follows_the_generators_sources_and_not_the_check(tmp_path: Path):
    copy = tmp_path / "scene"
    shutil.copytree(SCENE, copy, ignore=shutil.ignore_patterns("__pycache__"))
    before = drift.source_digest(copy)
    assert before == drift.source_digest()                       # the copy is read the way the checkout is
    (copy / "drift.py").write_text("# edited\n")
    assert drift.source_digest(copy) == before                   # the check is not an input
    (copy / "place.py").write_text((copy / "place.py").read_text() + "\n# edited\n")
    assert drift.source_digest(copy) != before                   # a generator module is


def test_the_manifest_the_generator_writes_carries_the_digest():
    """The generator needs Pillow, so read its writer as source: the digest is a key of the manifest it dumps."""
    assert '"source": source_digest()' in (SCENE / "output.py").read_text()
