"""A save's text as a format 8 or 9 encoder wrote it (engine DESIGN.txt, "Codec": FORMAT 9 dropped Mix.holds, FORMAT 10
made chips_seen counts), so a pin taken before either still checks today's encoding byte for byte."""
import json


def as_format_9(text: str) -> str:
    """`text`, an encoded save, with format 9 and each chips_seen count a flag."""
    doc: dict[str, dict[str, list[object]]] = json.loads(text)
    seen = [bool(s) for s in doc["save"]["chips_seen"]]
    return json.dumps({**doc, "format": 9, "save": {**doc["save"], "chips_seen": seen}}, sort_keys=True, separators=(",", ":"))


def as_format_8(text: str) -> str:
    """`text`, an encoded save, with format 8, chips_seen flags and an empty holds on every mix."""
    doc: dict[str, dict[str, list[dict[str, object]]]] = json.loads(as_format_9(text))
    mixes = [{**m, "holds": list[object]()} for m in doc["save"]["mixes"]]
    return json.dumps({**doc, "format": 8, "save": {**doc["save"], "mixes": mixes}}, sort_keys=True, separators=(",", ":"))
