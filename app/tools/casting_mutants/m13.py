"""Row 13 of MUTANTS.txt: order."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/work.py',
     '    save = marked(joined(installed(save, present_installs(save, rules, o.orders)), rules, o.joins), rules, o.marks)\n    save = cast_roles(save, rules, o.casts)\n',
     '    save = cast_roles(save, rules, o.casts)\n    save = marked(joined(installed(save, present_installs(save, rules, o.orders)), rules, o.joins), rules, o.marks)\n'),
]
