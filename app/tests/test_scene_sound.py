"""tools/scene: a layer says what it sounds as (docs/design/sound.md, "What wiring needs"): the fire's bed on the first
firelight, the evening piece on each evening's firelight, and nothing else."""
import sys
from pathlib import Path

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
import build   # tools/scene, on the path from the line above


def sounds() -> dict[str, str | None]:
    return {layer["id"]: layer.get("sound") for layer in build.light_layers()}


def test_the_first_firelight_sounds_as_the_fire_and_each_evenings_as_the_evening():
    got = sounds()
    assert got["firelight"] == "fire"
    evenings = [i for i in got if i.startswith("firelight_dusk")]
    assert len(evenings) > 1 and all(got[i] == "evening" for i in evenings)   # control: the evenings were found


def test_no_other_layer_sounds_as_anything():
    got = sounds()
    marked = {i for i, s in got.items() if s is not None}
    assert marked == {"firelight", *(i for i in got if i.startswith("firelight_dusk"))}
    assert got["firelight_fireback"] is None
