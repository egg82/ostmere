"""The stores the scene's layers and grades read: each `store:<id>` atom of a `when` or `until` in the scene manifest
on the assets volume (tools/scene/build.py writes it). Read by mtime, so a reseeded manifest is picked up unrestarted."""
import json
import logging
from pathlib import Path
from typing import Any

from .. import logs

_LOG = logging.getLogger("ashfall.scene")
_seen: dict[Path, tuple[int, frozenset[str]]] = {}


def scene_stores(manifest: Path | None) -> frozenset[str]:
    """Empty with no manifest (a host without the volume), or one that cannot be read, which is logged."""
    if manifest is None:
        return frozenset()
    try:
        stamp = manifest.stat().st_mtime_ns
    except OSError:
        return frozenset()
    known = _seen.get(manifest)
    if known is not None and known[0] == stamp:
        return known[1]
    stores: frozenset[str]
    try:
        stores = _stores_in(json.loads(manifest.read_text()))
    except (OSError, ValueError):
        logs.warning(_LOG, "scene.manifest_unreadable", path=str(manifest))
        stores = frozenset()
    _seen[manifest] = (stamp, stores)
    return stores


def _stores_in(manifest: dict[str, Any]) -> frozenset[str]:
    layers: list[dict[str, Any]] = manifest.get("layers", [])
    grades: dict[str, dict[str, Any]] = manifest.get("grades", {})
    conditions: list[str | None] = [c for layer in layers for c in (layer.get("when"), layer.get("until"))]
    conditions += [g.get("when") for g in grades.values()]
    atoms = [a for c in conditions if c for term in c.split("|") for a in term.split("&")]
    return frozenset(a[len("store:"):].partition("@")[0] for a in atoms if a.startswith("store:"))
