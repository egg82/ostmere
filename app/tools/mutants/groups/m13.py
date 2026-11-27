"""Row 13 of MUTANTS_groups.txt: a mark change removes the person's own shares from the town mix."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/people/marks.py',
     '            mix = _town_mix(rules, m.lane)\n',
     '            from ..core.index import index\n            from ..mixes.mixes import CardShare\n            save = replace(save, mixes=tuple(replace(x, components=tuple(c for c in x.components if not (isinstance(c, CardShare) and index(rules).cards[c.card].lane == m.lane))) for x in save.mixes))\n            mix = _town_mix(rules, m.lane)\n'),
]
