"""The completions the scene's layers show: each card a `project:` or `pushes:` atom of a layer's `when`/`until` names,
and each feature a `feature:` atom names. build.py writes them beside the generator as shown.json, which
app/tests/test_scene_shown.py reads to judge that every build the player can finish has a scene state."""
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

LIST = Path(__file__).with_name("shown.json")


def facts_shown(layers: Iterable[Mapping[str, Any]]) -> dict[str, list[str]]:
    conditions = [c for layer in layers for c in (layer.get("when"), layer.get("until"))]
    atoms = [a for c in conditions if c for term in c.split("|") for a in term.split("&")]
    kinds = [a.partition(":") for a in atoms]
    return {
        "cards": sorted({rest.partition("@")[0] for kind, _, rest in kinds if kind in ("project", "pushes")}),
        "features": sorted({rest for kind, _, rest in kinds if kind == "feature"}),
    }


def write_list(layers: Iterable[Mapping[str, Any]], path: Path = LIST) -> None:
    path.write_text(json.dumps(facts_shown(layers), indent=1) + "\n")
