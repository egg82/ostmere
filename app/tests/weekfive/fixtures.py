"""The engine contract suites' fixture worlds (casting, spells), loaded by path: the readings here are tested on the same
small worlds those suites were written on, so nothing is rebuilt by hand."""
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

CONTRACT = Path(__file__).resolve().parents[1] / "engine_contract"


def world(name: str, folder: str) -> ModuleType:
    """`<folder>/<name>.py` of the engine contract suite as a module (kept in sys.modules, so a second load is the first)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, CONTRACT / folder / f"{name}.py")
    assert spec is not None and spec.loader is not None, name
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
