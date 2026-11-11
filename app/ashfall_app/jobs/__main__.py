"""`python -m ashfall_app.jobs <name>`: run one job."""

import logging
import sys
from collections.abc import Callable

from .. import logs
from . import reminders

log = logging.getLogger("ashfall.jobs")

JOBS: dict[str, Callable[[], int]] = {"reminders": reminders.main}


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in JOBS:
        print(f"usage: python -m ashfall_app.jobs {{{'|'.join(JOBS)}}}", file=sys.stderr)
        return 2
    logs.setup()
    try:
        return JOBS[argv[0]]()
    except Exception:
        log.error("job.failed", extra={"fields": {"job": argv[0]}}, exc_info=True)   # the type chain, never a message
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
