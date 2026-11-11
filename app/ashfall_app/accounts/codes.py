"""Transfer codes (api/CONTRACT.txt, "Moving to another device"): eight characters of ALPHABET (about 40 bits), shown
"ABCD-EFGH", working once within LIFETIME. Stored only as "h1$" + HMAC-SHA256(ASHFALL_JOIN_KEY, the code), so a copied
database holds nothing to try without the key. The rows are db/codes.py; one live code per account, and each mint
sweeps a batch of expired ones (the writer enforces its own retention)."""

import hashlib
import hmac
import re
import secrets
from datetime import timedelta

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no I, O, 0 or 1: nothing to misread
LENGTH = 8
LIFETIME = timedelta(minutes=10)
SWEEP = 50   # expired codes deleted per mint
TRIES = 5   # fresh codes tried when one's hash is already stored
_LINK = re.compile(r"#join=([^#]*)$")
_GAPS = re.compile(r"[\s\-]+")


def make() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(LENGTH))


def shown(code: str) -> str:
    half = LENGTH // 2
    return code[:half] + "-" + code[half:]


def normal(typed: str) -> str | None:
    """A code as stored: from a join link, or typed in any case with or without spaces and dashes; else None."""
    text = typed.strip()
    link = _LINK.search(text)
    code = _GAPS.sub("", link.group(1) if link else text).upper()
    if len(code) != LENGTH or any(ch not in ALPHABET for ch in code):
        return None
    return code


def digest(key: bytes, code: str) -> bytes:
    return b"h1$" + hmac.new(key, code.encode(), hashlib.sha256).digest()
