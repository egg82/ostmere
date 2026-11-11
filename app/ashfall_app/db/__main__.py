"""`python -m ashfall_app.db migrate`: bring the database DATABASE_URL names to the newest revision (migrate.py)."""

import os
import sys

from .. import logs
from .migrate import migrate


def main(argv: list[str]) -> int:
    if argv != ["migrate"]:
        print("usage: python -m ashfall_app.db migrate", file=sys.stderr)
        return 2
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2
    logs.setup()
    migrate(url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
