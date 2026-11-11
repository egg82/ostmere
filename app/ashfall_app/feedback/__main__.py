"""Reads tester feedback back: `python -m ashfall_app.feedback list [--since DAYS]` prints each row, oldest first (id,
time, build, save, game time, the save's last line key, then the words indented). It needs only the app image and the
app's database environment. From a one-off pod, with `--context` naming your cluster:

IMG="$(kubectl --context site-a -n ashfall get deploy app -o jsonpath='{.spec.template.spec.containers[?(@.name=="app")].image}')"
kubectl --context site-a -n ashfall run fb --rm -i --restart=Never --image="$IMG" --overrides='{"spec":{"containers":[{"name":"fb","image":"'"$IMG"'","args":["python","-m","ashfall_app.feedback","list","--since","7"],"env":[{"name":"DATABASE_URL","value":"postgresql://postgres-rw/ashfall"},{"name":"PGUSER","valueFrom":{"secretKeyRef":{"name":"openbao","key":"username"}}},{"name":"PGPASSWORD","valueFrom":{"secretKeyRef":{"name":"openbao","key":"password"}}}]}]}}'

(The env is the app Deployment's own, from the cluster repo's app manifest.)"""

import argparse
import os
import re
import sys
from datetime import UTC, timedelta


from ..clock import system
from ..db import feedback as rows
from ..db.engine import open_database


_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def _safe(text: str) -> str:
    """The words with control characters shown as \\xNN: what a tester sent must not drive the owner's terminal."""
    return _CONTROL.sub(lambda m: f"\\x{ord(m.group()):02x}", text)


def render(r: rows.FeedbackRecord) -> str:
    head = (f"#{r.id} {r.created_at.astimezone(UTC):%Y-%m-%d %H:%M}Z build={r.build} save={r.save_id or '-'} "
            f"game_time={'-' if r.game_time is None else r.game_time} line={r.last_line or '-'}")
    return "\n".join([head, *("    " + _safe(ln) for ln in r.text.splitlines())])


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m ashfall_app.feedback")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list", help="print the feedback, oldest first")
    listing.add_argument("--since", type=int, metavar="DAYS", help="only the last DAYS days")
    args = parser.parse_args(argv)
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2
    since = None if args.since is None else system() - timedelta(days=args.since)
    database = open_database(url)
    try:
        with database.engine.connect() as conn:
            found = rows.listing(conn, since)
    finally:
        database.close()
    for r in found:
        print(render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
