"""A save's camp level (SaveInfo.camp_level) is how many of the content's Camp triggers have fired, and only those."""
from dataclasses import replace

from ashfall_app import engine as e
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.write import camp_level


def test_the_camp_level_counts_only_camp_triggers_that_fired(rs: Ruleset):
    camp = rs.camp_triggers
    assert len(camp) >= 2, "the opening has Camp levels: the probe needs some to count"
    others = [i for i in range(len(rs.rules.triggers)) if i not in camp]
    assert others, "control: triggers that are not the camp's"
    save = e.new_save(rs.rules)
    none = tuple(False for _ in rs.rules.triggers)
    assert camp_level(replace(save, fired=none), rs) == 0
    two = tuple(i in camp[:2] for i in range(len(none)))
    assert camp_level(replace(save, fired=two), rs) == 2
    rest = tuple(i in others for i in range(len(none)))
    assert camp_level(replace(save, fired=rest), rs) == 0
