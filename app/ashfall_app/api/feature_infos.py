"""The features' wire form: a carried bonus's label and what it does, and a feature's one-time card."""
from ..opening.feature_entries import FeatureCardEntry, FeatureEntry
from ..opening.schema import Opening
from . import feature_models as fm
from .changes import changes


def feature_info(o: Opening, f: FeatureEntry) -> fm.FeatureInfo:
    """A feature's effect is the answer that unlocks it: that answer's cost text and its modifiers' changes."""
    answer = next((a for x in o.offers for a in x.answers if a.outcome.modifiers
                   and any(u.unlock_kind == "feature" and u.id == f.id for u in a.outcome.unlocks)), None)
    return fm.FeatureInfo(feature=f.id, hint_key=f.hint_key, label_key=f.label_key, feature_card=_card(f.card),
                          effect_key=None if answer is None else answer.cost_key,
                          change_bp=[] if answer is None else changes(answer.outcome.modifiers))


def _card(card: FeatureCardEntry | None) -> fm.FeatureCard | None:
    if card is None:
        return None
    return fm.FeatureCard(title_key=card.title_key, line_keys=list(card.line_keys), button_key=card.button_key)
