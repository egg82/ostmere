"""The stores the scene reads: each `store:` atom of a layer's `when`/`until` or a grade's `when`. build.py writes them
beside the manifest as the app's scene_stores.json, which the API serves levels from (app/ashfall_app/api/world/scenestores.py)."""
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

APP_LIST = Path(__file__).resolve().parents[2] / "app" / "ashfall_app" / "api" / "world" / "scene_stores.json"


def stores_read(layers: Iterable[Mapping[str, Any]], grades: Mapping[str, Mapping[str, Any]]) -> list[str]:
    conditions = [c for layer in layers for c in (layer.get("when"), layer.get("until"))]
    conditions += [g.get("when") for g in grades.values()]
    atoms = [a for c in conditions if c for term in c.split("|") for a in term.split("&")]
    return sorted({a[len("store:"):].partition("@")[0] for a in atoms if a.startswith("store:")})


def write_list(layers: Iterable[Mapping[str, Any]], grades: Mapping[str, Mapping[str, Any]], path: Path = APP_LIST) -> None:
    path.write_text(json.dumps(stores_read(layers, grades), indent=1) + "\n")
