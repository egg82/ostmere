"""No function in the app grows past 80 lines: large functions are where bugs hide (habits held eight it had to split).
HELD starts empty and stays empty; a FastAPI `routes()` factory is a container of handlers, so its handlers are measured."""
import ast
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
LIMIT = 80


def over() -> set[str]:
    found: set[str] = set()
    for p in sorted(APP.glob("*_app/**/*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name != "routes":
                if (n.end_lineno or n.lineno) - n.lineno + 1 > LIMIT:
                    found.add(f"{p.relative_to(APP)}:{n.name}")
    return found


def test_the_gate_sees_the_app():
    assert any(APP.glob("*_app/**/*.py")), "no app files found: the size gate would pass on nothing"


def test_no_function_over_the_limit():
    assert not over(), f"over {LIMIT} lines (split it): {sorted(over())}"
