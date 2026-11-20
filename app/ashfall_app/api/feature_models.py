"""Wire models of a feature: what the player carries and the card shown when it unlocks."""
from pydantic import BaseModel


class FeatureCard(BaseModel):
    title_key: str
    line_keys: list[str]
    button_key: str
    """Its one button, which puts the card away."""


class FeatureInfo(BaseModel):
    feature: str
    hint_key: str | None
    """A banner shown once when the feature unlocks."""
    label_key: str | None
    """A thing the player carries, shown with the chips once the feature unlocks."""
    effect_key: str | None
    """What carrying it does: the cost_key of the answer whose outcome unlocks the feature and installs modifiers, its
    {pct} and {pct_b} filled from change_bp. Null for a feature no such answer unlocks."""
    change_bp: list[int]
    """That answer's modifiers as signed changes in basis points, as AnswerInfo.change_bp. Empty with no effect_key."""
    feature_card: FeatureCard | None
    """A card shown once when the feature unlocks, after what came with it (CONTRACT.txt, "A feature's card")."""
