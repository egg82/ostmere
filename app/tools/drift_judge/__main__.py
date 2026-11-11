"""python -m tools.drift_judge --brief [BEFORE_SHA]   (from app/, PYTHONPATH=.)

Prints one self-contained brief for a fresh Claude Code subagent to judge: the owner's direction, the commit subjects and the
readout diffs since ANCHOR. BEFORE_SHA is the tip main had before the merge just landed (default: HEAD's parent). With
no readout change since ANCHOR it prints one line saying so. Exits 0; 2 on a bad argument."""
import sys

from tools.drift_judge.inputs import gather
from tools.drift_judge.prompt import NOTHING, brief


def main(argv: list[str]) -> int:
    if not argv or argv[0] != "--brief" or len(argv) > 2:
        print(__doc__, file=sys.stderr)
        return 2
    found = gather(argv[1] if len(argv) == 2 else "")
    print(NOTHING if found is None else brief(found))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
