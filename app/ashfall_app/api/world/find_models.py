"""Wire model of a find's amount (contract/text-and-numbers.txt, "Text and numbers", {found}); the conventions in models.py hold here."""
from pydantic import BaseModel


class FindInfo(BaseModel):
    """The amount a find puts in a store, for the text of its line: `line_key`'s `{found}` is quantity in whole items."""

    line_key: str
    store: str
    quantity: int
