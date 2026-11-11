"""Format upgrades: one function per old FORMAT, chained on the envelope's JSON before anything is decoded.

Semantics: DESIGN.txt, "FORMAT is 6", "Codec" in part "TOWNSFOLK, INSTALLED RULES AND OFFERS" (FORMAT 7), and
"Speed" (FORMAT 8) and "Codec" (FORMAT 9). UPGRADES[f] turns an envelope of format f into one of format f + 1. Every format
from OLDEST_FORMAT below FORMAT has an entry (tests/engine/test_rebase_impl.py and the release lock check it).
"""
from collections.abc import Callable

from .codec import FORMAT, Json
from .errors import StateFormatError

OLDEST_FORMAT = 4
"""The first format a rebase reads: the first one with a manifest. Older texts (the preview's tabs) are never rebased."""



def _chips_seen(envelope: Json) -> Json:
    """Format 4 to 5: the save gains chips_seen, one per manifest chip, True for a chip latched now or in the save's
    unlock set. A format 4 save cannot tell a chip that showed and cleared from one that never showed, so every chip it
    may have shown counts as seen: its on_line is never played twice, at the cost of one never played."""
    if not isinstance(envelope, dict) or not isinstance(save := envelope.get("save"), dict) \
            or not isinstance(manifest := envelope.get("manifest"), dict) or not isinstance(ids := manifest.get("chips"), list) \
            or not isinstance(chips := save.get("chips"), list) or not isinstance(unlocked := save.get("unlocked"), list):
        raise StateFormatError("not a format 4 save envelope")
    chip = {"@": "UnlockKind", "v": "chip"}
    shown = {str(u.get("id")) for u in unlocked if isinstance(u, dict) and u.get("kind") == chip}
    seen: list[Json] = [latch is True or str(c) in shown for c, latch in zip(ids, chips)]
    return {**envelope, "format": 5, "save": {**save, "chips_seen": seen}}


def _no_failed_attempts(envelope: Json) -> Json:
    """Format 5 to 6: a lane no longer holds a failed attempt (a failed tap takes no time), so each LaneState loses
    failed and failed_timer, and a lane that held a failed attempt is free. The attempt's line is not said."""
    if not isinstance(envelope, dict) or not isinstance(save := envelope.get("save"), dict) \
            or not isinstance(lanes := save.get("lanes"), list):
        raise StateFormatError("not a format 5 save envelope")
    kept: list[Json] = []
    for ls in lanes:
        if not isinstance(ls, dict) or not isinstance(failed := ls.get("failed"), bool) or "failed_timer" not in ls:
            raise StateFormatError("not a format 5 lane")
        rest = {k: v for k, v in ls.items() if k not in ("failed", "failed_timer")}
        kept.append({**rest, "card": None} if failed else rest)
    return {**envelope, "format": 6, "save": {**save, "lanes": kept}}


def _no_offers(envelope: Json) -> Json:
    """Format 6 to 7: the manifest gains "offers", empty. A format 6 save predates offers, so its unlock set holds no
    offer, answered or answer unlock and its orders and queue no AnswerOffer: nothing else changes."""
    if not isinstance(envelope, dict) or not isinstance(manifest := envelope.get("manifest"), dict) \
            or "offers" in manifest:
        raise StateFormatError("not a format 6 save envelope")
    return {**envelope, "format": 7, "manifest": {**manifest, "offers": []}}


def _no_kept_speed(envelope: Json) -> Json:
    """Format 7 to 8: each LaneState gains speed, None, so a tap a format 7 save began reads the live stack to its end,
    as it did when it began (DESIGN.txt, "Speed")."""
    if not isinstance(envelope, dict) or not isinstance(save := envelope.get("save"), dict) \
            or not isinstance(lanes := save.get("lanes"), list):
        raise StateFormatError("not a format 7 save envelope")
    if not all(isinstance(ls, dict) and "speed" not in ls for ls in lanes):
        raise StateFormatError("not a format 7 lane")
    kept: list[Json] = [{**ls, "speed": None} for ls in lanes if isinstance(ls, dict)]
    return {**envelope, "format": 8, "save": {**save, "lanes": kept}}


def _no_holds(envelope: Json) -> Json:
    """Format 8 to 9: each saved Mix loses holds, so a mix that held a card runs it at its full share."""
    if not isinstance(envelope, dict) or not isinstance(save := envelope.get("save"), dict) \
            or not isinstance(mixes := save.get("mixes"), list):
        raise StateFormatError("not a format 8 save envelope")
    if not all(isinstance(m, dict) and "holds" in m for m in mixes):
        raise StateFormatError("not a format 8 mix")
    kept: list[Json] = [{k: v for k, v in m.items() if k != "holds"} for m in mixes if isinstance(m, dict)]
    return {**envelope, "format": 9, "save": {**save, "mixes": kept}}


UPGRADES: dict[int, Callable[[Json], Json]] = {
    4: _chips_seen, 5: _no_failed_attempts, 6: _no_offers, 7: _no_kept_speed, 8: _no_holds}


def missing_upgrades() -> list[int]:
    """Formats from OLDEST_FORMAT below FORMAT with no UPGRADES entry: each one a release-blocking gap."""
    return [f for f in range(OLDEST_FORMAT, FORMAT) if f not in UPGRADES]


def upgrade(envelope: Json) -> dict[str, Json]:
    """The envelope at FORMAT, each step through UPGRADES; StateFormatError for a format outside [OLDEST_FORMAT,
    FORMAT] or an upgrade that does not land on the next format."""
    found = _format(envelope)
    while True:
        if not isinstance(envelope, dict) or envelope.get("format") != found:
            raise StateFormatError(f"an upgrade did not give format {found}")
        if found == FORMAT:
            return envelope
        if found not in UPGRADES:
            raise StateFormatError(f"no upgrade from format {found}")
        envelope = UPGRADES[found](envelope)
        found += 1


def _format(envelope: Json) -> int:
    fmt = envelope.get("format") if isinstance(envelope, dict) else None
    if not isinstance(fmt, int) or isinstance(fmt, bool) or not OLDEST_FORMAT <= fmt <= FORMAT:
        raise StateFormatError(f"format {fmt!r} cannot be rebased (readable: {OLDEST_FORMAT} to {FORMAT})")
    return fmt
