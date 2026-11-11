"""Recovery words (api/CONTRACT.txt, "Moving to another device"; habits' signin/keys.py): four words of the BIP-39
English list (words.txt, 2048 words, so 44 bits), shown once and stored only as "s1$" + scrypt, salted with
ASHFALL_JOIN_KEY so a copied database is no shortcut without the key. Deterministic (one salt), since the words alone
find their account: there is no name to type. scrypt at these costs holds 16 MiB while it runs, so a pod hashes at
most HASHING at once and a request that waits WAIT for a turn is told to try again (Busy)."""

import hashlib
import re
import secrets
import threading
from pathlib import Path

WORDS = tuple((Path(__file__).resolve().parent / "words.txt").read_text().split())
WORD_SET = frozenset(WORDS)
COUNT = 4
SALT = b"ashfall-words-v1"
HASHING, WAIT = 2, 3.0
BUSY_RETRY_S = 3
_SPLIT = re.compile(r"[\s\-.,_]+")


class Busy(Exception):
    """Every turn at hashing words was taken for WAIT seconds."""


def make() -> str:
    return "-".join(secrets.choice(WORDS) for _ in range(COUNT))


def normal(typed: str) -> str | None:
    """Words as stored, from any case and any run of spaces, dashes, dots, commas or underscores; else None."""
    words = [w for w in _SPLIT.split(typed.strip().lower()) if w]
    return "-".join(words) if len(words) == COUNT and all(w in WORD_SET for w in words) else None


class Hashing:
    """The pod's turns at hashing words (per pod by design: it bounds this process's memory)."""

    def __init__(self, turns: int = HASHING, wait: float = WAIT) -> None:
        self._turns, self._wait = threading.BoundedSemaphore(turns), wait

    def digest(self, key: bytes, words: str) -> bytes:
        if not self._turns.acquire(timeout=self._wait):
            raise Busy()
        try:
            return b"s1$" + hashlib.scrypt(words.encode(), salt=key + SALT, n=2 ** 14, r=8, p=1, dklen=32)
        finally:
            self._turns.release()
