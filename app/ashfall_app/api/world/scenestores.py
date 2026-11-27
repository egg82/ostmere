"""The stores the scene's layers and grades read in a `store:` condition. tools/scene/build.py writes the list
(scene_stores.json, beside this module) from the same layers it seeds, so the API needs no assets volume."""
import json
from functools import cache
from pathlib import Path


@cache
def scene_stores() -> frozenset[str]:
    return frozenset(json.loads((Path(__file__).with_name("scene_stores.json")).read_text()))
