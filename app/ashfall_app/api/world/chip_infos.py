"""The chips' wire form (Content.chip_infos): when each shows, what it costs, its lines, and whether it is a season's
chore."""
from ... import engine as e
from ...opening import convert as authored
from ...opening.chores import chores
from ...opening.schema import Opening
from . import content_models as cm
from .. import convert
from .changes import changes


def chip_infos(o: Opening, rules: e.Rules) -> list[cm.ChipInfo]:
    cards = {x.id for x in o.cards}
    chore_chips = set(chores(o, rules))
    return [cm.ChipInfo(chip=c.id, label_key=c.label_key, tone=c.tone,
                        when=convert.condition(authored.condition(c.when, cards)), cost_key=c.cost_key,
                        change_bp=changes(c.effects), on_line_key=c.on_line_key, off_line_keys=c.off_line_keys,
                        offered_after=None if c.offered_after is None
                        else convert.unlock(authored.unlock(c.offered_after)),
                        chore=c.id in chore_chips) for c in o.chips]
