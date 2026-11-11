"""A save's text as a format 8 encoder wrote it (engine DESIGN.txt, "Codec": FORMAT 9 dropped Mix.holds), so a pin
taken before FORMAT 9 still checks today's encoding byte for byte."""
import json


def as_format_8(text: str) -> str:
    """`text`, an encoded save, with format 8 and an empty holds on every mix."""
    doc: dict[str, dict[str, list[dict[str, object]]]] = json.loads(text)
    mixes = [{**m, "holds": list[object]()} for m in doc["save"]["mixes"]]
    return json.dumps({**doc, "format": 8, "save": {**doc["save"], "mixes": mixes}}, sort_keys=True, separators=(",", ":"))
