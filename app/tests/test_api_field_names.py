"""One field name, one type, API-wide (contract-first API design): across every wire model in
ashfall_app/api/models.py, decision_models.py, content_models.py and camp_models.py a field name resolves to a single type, list item types included. A
generated client gives one name one type; two models disagreeing about `store` or `orders` is a client that cannot compile or silently
coerces. Optionality is not a type: `x: int` and `x: int | None` agree. A `kind: Literal[...]` discriminator is its
value type, as the module docstring says it is only ever a union's discriminator string."""
import inspect
from types import NoneType, UnionType
from typing import Annotated, Literal, TypeAliasType, Union, get_args, get_origin

from pydantic import BaseModel

from ashfall_app.api import camp_models, content_models, decision_models, models
from ashfall_app.api.models import Mix, Order, QueueEntry


def _leaves(tp: object) -> set[str]:
    """The distinct types a field may hold, aliases and Annotated unwrapped, unions flattened, None dropped."""
    if isinstance(tp, TypeAliasType):
        return _leaves(tp.__value__)
    origin = get_origin(tp)
    if origin is Annotated:
        return _leaves(get_args(tp)[0])
    if origin is Literal:
        return {type(v).__name__ for v in get_args(tp)}
    if origin is Union or origin is UnionType:
        members: set[str] = set()
        for a in get_args(tp):
            if a is not NoneType:
                members |= _leaves(a)
        return members
    if origin is not None:
        items = ", ".join(_type_name(a) for a in get_args(tp))
        return {f"{getattr(origin, '__name__', repr(origin))}[{items}]"}
    if isinstance(tp, type):
        return {tp.__name__}
    return {repr(tp)}


def _type_name(tp: object) -> str:
    return " | ".join(sorted(_leaves(tp)))


def _wire_models(module: object) -> list[type[BaseModel]]:
    found: list[type[BaseModel]] = []
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if issubclass(cls, BaseModel) and cls.__module__ == getattr(module, "__name__"):
            found.append(cls)
    return found


def _by_name(classes: list[type[BaseModel]]) -> dict[str, dict[str, list[str]]]:
    """field name -> type name -> the `Model.field` places that declare it."""
    groups: dict[str, dict[str, list[str]]] = {}
    for cls in classes:
        for name, info in cls.model_fields.items():
            groups.setdefault(name, {}).setdefault(_type_name(info.annotation), []).append(f"{cls.__name__}.{name}")
    return groups


def _conflicts(classes: list[type[BaseModel]]) -> dict[str, dict[str, list[str]]]:
    return {name: types for name, types in _by_name(classes).items() if len(types) > 1}


def test_every_field_name_has_one_type_across_the_api_models():
    classes = [cls for m in (models, decision_models, content_models, camp_models) for cls in _wire_models(m)]
    groups = _by_name(classes)
    # The check can see something: many models, and names that several models share (else "no conflicts" is vacuous).
    assert len(classes) >= 30 and len(groups) >= 80
    shared = {name for name, types in groups.items() if sum(len(places) for places in types.values()) >= 2}
    assert {"store", "action", "at", "card", "when", "orders"} <= shared
    assert _conflicts(classes) == {}


def test_the_check_fails_on_a_planted_conflicting_field():
    """The probe can return non-zero: a throwaway model reusing `store` as an int, one reusing `orders` with another
    item type, and one reusing `chips` as a list of ints each show up as a conflict naming both places; a field that
    differs only by being nullable does not."""

    class PlantedStore(BaseModel):
        store: int

    class PlantedOrders(BaseModel):
        orders: list[Mix]

    class PlantedChips(BaseModel):
        chips: list[int]

    class PlantedNullable(BaseModel):
        limit: int
        next_event_at: int

    class Agrees(BaseModel):
        orders: list[Order]
        entries: list[QueueEntry]

    real = _wire_models(models)
    assert _conflicts(real) == {}
    conflicts = _conflicts(real + [PlantedStore, PlantedOrders, PlantedChips, PlantedNullable, Agrees])
    assert set(conflicts) == {"store", "orders", "chips"}
    assert "PlantedStore.store" in conflicts["store"]["int"] and "Step.state" not in conflicts["store"]["int"]
    assert "PlantedOrders.orders" in conflicts["orders"]["list[Mix]"]
    assert "View.orders" in conflicts["orders"]["list[Order]"]
    assert "PlantedChips.chips" in conflicts["chips"]["list[int]"]
    assert "View.chips" in conflicts["chips"]["list[str]"]
