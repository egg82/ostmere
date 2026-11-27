"""Where the people are: every outcome that joins or leaves a person, or marks one as doing something the scene could show
(`doings`), and every marked line no outcome carries (`[line_doings]`), names the scene layer that shows it or says why none
does (`whereabouts`, entries.WhereaboutsEntry). A case is `<owner>:<person>`, the owner being `trigger:<id>`,
`card:<id>/outcome`, `card:<id>/finished`, `offer:<offer>/<answer>` or `line:<key>`.
app/tests/scene/test_scene_people.py holds every join, leave and doing to the field, and the held cases to the audit."""

HELD_UNPLACED: frozenset[str] = frozenset()
"""Cases that join, leave or set a person doing something the scene shows nothing of today (the audit, one row each):
may only shrink. A case leaves this list when its outcome gains a `whereabouts` entry for the person."""

HELD_LINE_ONLY: frozenset[str] = frozenset()
"""Cases of a line no outcome carries (`[line_doings]`, `line:<key>:<person>`) that the scene shows nothing of today: may
only shrink. A case leaves this list when its line's `whereabouts` gains an entry for the person."""
