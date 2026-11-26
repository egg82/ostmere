"""Data kept on a Rules object and computed once (an immutable value, found by identity: index.py)."""
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rules import Rules


def derived[T](rules: "Rules", name: str, build: Callable[["Rules"], T]) -> T:
    """build(rules), computed once per rules object and kept on it under `name`."""
    kept = vars(rules)
    if name not in kept:
        kept[name] = build(rules)
    found: T = kept[name]
    return found
