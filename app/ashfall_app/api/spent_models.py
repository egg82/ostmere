"""A spent card's share on the wire (CONTRACT.txt, "SPENT"; re-exported from models.py)."""
from pydantic import BaseModel


class SpentShare(BaseModel):
    """The part, share_bp, of spent card `card`'s share that the card holding this entry runs now."""

    card: str
    share_bp: int
