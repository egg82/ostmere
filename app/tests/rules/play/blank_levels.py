"""The levels that pay nothing (docs/design/sim-invariants.md, O14): a level in a skill's row with no marker drawn, and a
level of a later phase no trigger waits for. A figure for the opening's readout (report.py), never a check: that every
level pays is taste. What a drawn marker shows is kept by `unpaid_markers` (test_level_pays.py)."""
from ashfall_app.rules.schema import Opening
from ashfall_app.engine import Rules


def top_level(rules: Rules) -> int:
    return len(rules.curve.thresholds) + 1


def mixed_skills(rules: Rules) -> set[str]:
    """The skills a hands card trains: the mix drives them."""
    return {str(c.skill) for c in rules.cards if c.skill is not None and str(c.lane) == "hands"}


def row_blanks(o: Opening, rules: Rules) -> dict[str, list[int]]:
    """Per skill, the levels before its row's last marker with none drawn; a mixed skill's row runs to the curve's top."""
    mixed = mixed_skills(rules)
    out: dict[str, list[int]] = {}
    for s in o.skills:
        marked = {lv.level for lv in s.levels}
        last = top_level(rules) if s.id in mixed else max(marked, default=1)
        out[s.id] = [n for n in range(2, last + 1) if n not in marked]
    return out


def unmarked_levels(o: Opening, rules: Rules) -> list[str]:
    return [f"{skill} {n}" for skill, levels in row_blanks(o, rules).items() for n in levels]


def level_pays(o: Opening, skill: str) -> set[int]:
    """The counted levels a skill's triggers wait for."""
    return {t.when.value for t in o.triggers if t.when.subject_kind == "skill_level" and t.when.id == skill}


def phase_blanks(o: Opening) -> dict[str, list[int]]:
    """Per later-phase skill, the levels its track reaches past the first phase's top that no trigger waits for."""
    assert o.prestige is not None
    top = o.prestige.top_level
    out: dict[str, list[int]] = {}
    for pp in o.phase_pays:
        ranks = sum(n.ranks for n in o.nodes if n.skill == pp.skill)
        out[pp.skill] = sorted(set(range(top + 1, ranks * (top - 1) + top + 1)) - level_pays(o, pp.skill))
    return out


def blank_lines(o: Opening, rules: Rules) -> list[str]:
    """Per skill, the levels paying nothing in its row and in the later phases its track reaches."""
    row, phase = row_blanks(o, rules), phase_blanks(o)
    return [f"  {s.id:14s} row {row[s.id] or 'none'}; later phases {phase[s.id] if s.id in phase and phase[s.id] else 'none'}"
            for s in o.skills]
