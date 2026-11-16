"""The writer's client: what answers a job. NullClient is the default, so the game runs with no API key: it returns the
authored stand-in. A live client is a later step and implements the same Protocol."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class JobKind:
    """One kind of thing the writer writes. `name` is the id logs and budgets key on."""

    name: str


class Client(Protocol):
    def write(self, kind: JobKind, stand_in: str) -> str:
        """The text for one job. `stand_in` is the authored line the game plays when nothing better exists. Raises
        on any failure; the Writer answers with the stand-in then."""
        ...


class NullClient:
    def write(self, kind: JobKind, stand_in: str) -> str:
        return stand_in
