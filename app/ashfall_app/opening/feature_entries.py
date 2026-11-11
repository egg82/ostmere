"""The content file's feature and aim entries (schema.Opening and schema.Chapter hold them beside entries.py's): what the
player carries, a feature's card, and the stretch of play's stated aim."""
from .entries import Entry, UnlockEntry


class FeatureCardEntry(Entry):
    """A card over the panel's foot, shown once when its feature unlocks, after what came with it: a title, its lines
    and one button that puts it away (api/CONTRACT.txt, "A feature's card")."""

    title_key: str
    line_keys: list[str]
    button_key: str


class FeatureEntry(Entry):
    id: str
    hint_key: str | None = None
    label_key: str | None = None
    """A thing the player carries, shown with the chips once unlocked."""
    card: FeatureCardEntry | None = None


class AimEntry(Entry):
    """What the current stretch of play is for, in the story's voice, shown as one line at the band's top
    (docs/decisions.md, "Every stretch of play has a stated aim"). It holds from `after` until a later aim's `after`
    is unlocked: the page shows the last aim in content order whose `after` view.unlocked holds. Only the first aim
    has none, so one is always set."""

    id: str
    text_key: str
    after: UnlockEntry | None = None
