"""Whether the scene art served live is the art this checkout's generator builds.

The generator writes `source_digest()` into the manifest it seeds onto the assets volume; this script (stdlib only, no
Pillow or art packs needed) recomputes the digest from the checkout and compares it with the manifest served live.

    python tools/scene/drift.py [MANIFEST_URL]

Exit 0 when they match, 42 when the live manifest was built from other code (or carries no digest), 43 when it could
not be read. It only reports: it never reseeds. The art packs are outside git and not part of the digest.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = "https://ostmere.yggdrasil.pub/assets/art/scene/manifest.json"
MATCH, DRIFT, UNREADABLE = 0, 42, 43


def source_digest(scene: Path = HERE) -> str:
    """The generator's inputs: every module beside this one except this one, so editing the check reseeds nothing."""
    h = hashlib.sha256()
    for path in sorted(scene.glob("*.py")):
        if path.name != Path(__file__).name:
            h.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def compare(served: object, expected: str) -> tuple[int, str]:
    if served == expected:
        return MATCH, f"scene art matches the code: source={expected}"
    if served is None:
        return DRIFT, f"scene art on the volume carries no source digest (built before the digest); code expects {expected}"
    return DRIFT, f"scene art is stale: volume source={served}, code expects {expected}; reseed it (seed-assets-job.yaml)"


def check(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            manifest: dict[str, object] = json.load(r)
        served = manifest.get("source")
    except (OSError, ValueError, AttributeError) as e:   # unreachable, not JSON, or JSON that is not an object
        return UNREADABLE, f"could not read a manifest from {url}: {e}"
    return compare(served, source_digest())


def main() -> None:
    code, line = check(sys.argv[1] if len(sys.argv) > 1 else LIVE)
    print(line)
    sys.exit(code)


if __name__ == "__main__":
    main()
