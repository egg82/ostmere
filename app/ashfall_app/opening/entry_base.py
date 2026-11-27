"""The base of every content entry."""
from pydantic import BaseModel, ConfigDict


class Entry(BaseModel):
    """Content is our own file one directory away: an unknown field is a typo, so it fails the load."""

    model_config = ConfigDict(extra="forbid")
