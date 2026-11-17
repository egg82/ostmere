"""The committed list of paths the playthrough tests depend on covers what is computed from the code now.

CI's `changes` job runs the playthroughs when a pull request touches a listed path, so a path missing here is a change
that merges without them. Regenerate: python -m tools.playthrough_paths --write (from app/).
"""
from tools.playthrough_paths import committed, computed, covers


def test_the_committed_list_covers_what_the_playthroughs_depend_on() -> None:
    listing = committed()
    missing = [path for path in computed() if not covers(listing, path)]
    assert not missing, f"not in app/tools/playthrough_paths.txt (regenerate it): {missing}"


def test_a_path_taken_out_of_the_list_is_seen_missing() -> None:
    listing = committed()
    assert listing, "an empty list would pass the check above only by covering nothing it was asked"
    exact = next(path for path in listing if not path.endswith("/"))
    assert covers(listing, exact)
    assert not covers([p for p in listing if p != exact], exact)
    assert covers(listing, "content/anything/at/all.md") and not covers(listing, "docs/engineering.md")
