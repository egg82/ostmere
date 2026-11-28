"""tools/scene/frame/grades.py against the content: every hidden night clock (a store marked `clock = "night"` and
`hidden`, which exists only for the scene's night grade) is read by a dark grade, every season turn's feature by a day
grade, and each turn's light is later in the list than every earlier chapter's night and earlier than its own and later
chapters' nights (the page's chooseGrade shows the last grade whose `when` holds, and a night clock stays full)."""
import sys
import tomllib
from pathlib import Path

from ashfall_app.rules.schema import CHAPTERS, load_opening

SCENE = Path(__file__).resolve().parent.parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))
from frame.conditions import holds   # tools/scene, on the path from the line above
from frame.grades import GRADES, pick
from frame.stages import STAGES

ORDER = list(GRADES)


def atoms(when: object) -> set[str]:
    if not isinstance(when, str):
        return set()
    return {a.split("@")[0] for alt in when.split("|") for a in alt.split("&")}


def readers(atom: str, dark: bool) -> list[str]:
    return [g for g, spec in GRADES.items() if atom in atoms(spec["when"]) and bool(spec.get("dark")) == dark]


def hidden_night_clocks() -> list[str]:
    return [s.id for s in load_opening().stores if s.clock == "night" and s.hidden]


def season_features() -> list[str]:
    return [u.id for t in load_opening().triggers if t.season for u in t.outcome.unlocks if u.unlock_kind == "feature"]


def test_the_content_has_nights_and_turns_to_check():
    assert len(hidden_night_clocks()) >= 2 and len(season_features()) >= 2


def test_every_hidden_night_clock_has_a_night_grade():
    missing = [n for n in hidden_night_clocks() if not readers(f"store:{n}", dark=True)]
    assert not missing, f"hidden night clocks no dark grade reads: {missing}"


def test_every_season_turn_has_its_light():
    missing = [f for f in season_features() if not readers(f"feature:{f}", dark=False)]
    assert not missing, f"season turns no day grade reads: {missing}"


def chapter_of() -> dict[str, int]:
    """Each hidden night clock's and season turn feature's chapter, in calendar order (CHAPTERS); a chapter's season
    turn is its first day's, before its nights."""
    at: dict[str, int] = {}
    for i, path in enumerate(CHAPTERS):
        data = tomllib.loads(path.read_text())
        at |= {f"store:{s['id']}": i for s in data.get("stores", []) if s.get("clock") == "night" and s.get("hidden")}
        at |= {f"feature:{u['id']}": i for t in data.get("triggers", []) if t.get("season")
               for u in t["outcome"].get("unlocks", []) if u["unlock_kind"] == "feature"}
    return at


def test_each_turn_ends_the_nights_before_it_and_not_after():
    """A night clock stays full once its hour has run, so a night grade later in the list than a later turn's light
    shows all day after it (week two's last night did, through weeks three and four), and a turn's light later in the
    list than its own nights hides them."""
    at = chapter_of()
    assert {f"store:{n}" for n in hidden_night_clocks()} | {f"feature:{f}" for f in season_features()} <= set(at)
    wrong: list[tuple[str, str]] = []
    for turn in (a for a in at if a.startswith("feature:")):
        light = min(ORDER.index(g) for g in readers(turn, dark=False))
        for night in (a for a in at if a.startswith("store:")):
            for g in readers(night, dark=True):
                if (at[night] < at[turn]) != (ORDER.index(g) < light):
                    wrong.append((turn, g))
    assert not wrong, wrong


def test_the_week_three_and_four_stages_show_their_light():
    shown = {name: pick(lambda when, s=STAGES[name]: holds(when, s)) for name in
             ("53_clear", "54_dusk_15", "54_frost_night", "54_day_16", "66_night_21", "66_dawn_22", "67_still",
              "72_dusk_24", "72_night_24", "72_day_25", "71_names_night")}
    assert shown == {"53_clear": "clear", "54_dusk_15": "dusk_15", "54_frost_night": "night_15", "54_day_16": "day_16",
                     "66_night_21": "night_21", "66_dawn_22": "day_22", "67_still": "still", "72_dusk_24": "dusk_24",
                     "72_night_24": "night_24", "72_day_25": "day_25", "71_names_night": "night_28"}
