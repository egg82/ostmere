"""tools.readouts_pull copies a run's readouts in and refuses any name that is not a readout's."""
from pathlib import Path

from tools.readouts_pull import accepted, copy_in


def test_names():
    assert accepted("dayone-typical.txt") and accepted("opening.txt") and accepted("weektwo-eight-sharp.txt")
    for bad in ("ANCHOR", "evil.txt", "dayone-typical.sh", "../dayone.txt", "dayone-x/y.txt", ".txt", "dayone-.txt"):
        assert not accepted(bad), bad


def test_copy_in_across_artifact_folders(tmp_path: Path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    (src / "readouts-new-a-0").mkdir(parents=True)
    (src / "readouts-new-b").mkdir()
    dst.mkdir()
    (src / "readouts-new-a-0" / "dayone-typical.txt").write_text("new\n")
    (src / "readouts-new-b" / "ANCHOR").write_text("x")
    (src / "readouts-new-b" / "other.txt").write_text("x")
    (src / "readouts-new-a-0" / "opening.txt").write_text("new\n")
    (dst / "dayone").mkdir()
    (dst / "dayone" / "dayone-typical.txt").write_text("old\n")
    written, refused = copy_in(src, dst)
    assert written == [dst / "dayone" / "dayone-typical.txt", dst / "rules" / "opening.txt"]
    assert all(f.read_text() == "new\n" for f in written)
    assert refused == ["readouts-new-b/ANCHOR", "readouts-new-b/other.txt"]
    assert sorted(str(p.relative_to(dst)) for p in dst.rglob("*.txt")) == ["dayone/dayone-typical.txt", "rules/opening.txt"]
