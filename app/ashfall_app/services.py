"""The service locator (docs/systems.md): which implementation answers each system. One instance per app, built by its
entry point (main.py) and held on app.state.services; every field defaults to its Null Object, so an entry point that
wires nothing gets systems that answer "nobody" and "unavailable", never a plausible wrong answer. Callers hold the
interfaces named here, never an implementation."""

from dataclasses import dataclass, field

from fastapi import Request

from .accounts.interface import Accounts, NullAccounts
from .saves.interface import NullSaves, Saves


@dataclass(frozen=True)
class Services:
    accounts: Accounts = field(default_factory=NullAccounts)
    saves: Saves = field(default_factory=NullSaves)


def of(request: Request) -> Services:
    """The services of the app a request reached."""
    found = getattr(request.app.state, "services", None)
    return found if isinstance(found, Services) else Services()
