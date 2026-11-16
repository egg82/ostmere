"""Writer: the registry of job kinds, a client, and the one logfmt line per call."""

import logging
import time

from .. import logs
from .interface import Client, JobKind, NullClient

log = logging.getLogger("ashfall.writer")


class UnknownKind(KeyError):
    """A job named a kind nobody registered: a programming error, never a runtime condition."""


class Registry:
    def __init__(self, kinds: tuple[JobKind, ...] = ()) -> None:
        self._kinds: dict[str, JobKind] = {}
        for k in kinds:
            self.add(k)

    def add(self, kind: JobKind) -> None:
        if kind.name in self._kinds:
            raise ValueError(f"job kind registered twice: {kind.name}")
        self._kinds[kind.name] = kind

    def get(self, name: str) -> JobKind:
        try:
            return self._kinds[name]
        except KeyError:
            raise UnknownKind(name) from None


class Writer:
    def __init__(self, registry: Registry | None = None, client: Client | None = None) -> None:
        self.registry = registry or Registry()
        self.client = client or NullClient()

    def write(self, kind_name: str, stand_in: str) -> str:
        """The text for a job of a registered kind. A client failure is logged and answered with the stand-in, so
        nothing the player sees ever errors. The line names the kind, outcome and duration, never the text."""
        kind = self.registry.get(kind_name)
        t0 = time.perf_counter()
        try:
            text = self.client.write(kind, stand_in)
        except Exception:
            log.warning("writer.call", extra={"fields": self._fields(kind, "failed", t0)}, exc_info=True)
            return stand_in
        logs.info(log, "writer.call", **self._fields(kind, "ok", t0))
        return text

    def _fields(self, kind: JobKind, outcome: str, t0: float) -> dict[str, object]:
        return {"kind": kind.name, "outcome": outcome, "client": type(self.client).__name__,
                "ms": int((time.perf_counter() - t0) * 1000)}
