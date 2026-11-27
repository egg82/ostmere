"""A card's site (entries.CardEntry.site): kept apart from entries.py, which is at its size limit."""
from pydantic import BaseModel, ConfigDict, model_validator


class SiteEntry(BaseModel):
    """Where a card's work is done, as the scene shows it (app/tests/test_scene_sites.py): `layer` is the id of the scene
    layer a person working the card stands at, `no_site` the reason there is no one place. Exactly one; words only to the
    engine."""

    model_config = ConfigDict(extra="forbid")

    layer: str | None = None
    no_site: str | None = None

    @model_validator(mode="after")
    def _one_answer(self) -> "SiteEntry":
        if (self.layer is None) == (self.no_site is None):
            raise ValueError("site: name exactly one of layer and no_site")
        return self
