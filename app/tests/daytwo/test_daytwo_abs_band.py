"""The beat reader (abs_band.py) on planted landing histories and on beats.yaml itself: days are counted from the save's
start, each beat's target_day and the pace_scale are read off beats.yaml and follow its edits, a beats.yaml without
the numbers is refused, and a route that reaches no beat from B5 says so."""
import re
from pathlib import Path

import pytest

from tests.daytwo import abs_band
from tests.dayone.beats import BEATS_YAML

PACE = abs_band.load_pace()
BEAT = "B5"
D = PACE.targets[BEAT]
S = PACE.scale
DAY = abs_band.DAY_S


def test_the_numbers_are_read_off_beats_yaml():
    text = BEATS_YAML.read_text()
    assert S == float(text.split("\npace_scale:", 1)[1].split()[0]) and S > 0
    assert D == 4 and BEAT in PACE.targets and "B4" not in PACE.targets


def test_days_count_from_the_saves_start():
    assert abs_band.reached({BEAT: 7 * DAY}, 7 * DAY, PACE) == {BEAT: 0.0}
    assert abs_band.reached({BEAT: 7 * DAY + DAY // 2, "B4": 0}, 7 * DAY, PACE) == {BEAT: 0.5}


def test_a_line_names_each_beat_its_day_and_its_target_day():
    line = abs_band.summary("typical", {BEAT: 3.5}, PACE)
    assert f"{BEAT} day 3.5, target_day {D}" in line and f"pace_scale {S:g}" in line


def test_a_changed_pace_scale_and_target_day_are_read(tmp_path: Path):
    edited = tmp_path / "beats.yaml"
    text = re.sub(r"^pace_scale:.*$", f"pace_scale: {2 * S:g}", BEATS_YAML.read_text(), count=1, flags=re.M)
    edited.write_text(text.replace("{id: B5, region: R1, target_day: 4,", "{id: B5, region: R1, target_day: 9,", 1))
    pace = abs_band.load_pace(edited)
    assert pace.scale == 2 * S and pace.targets[BEAT] == 9


def test_a_beats_yaml_without_the_numbers_is_refused(tmp_path: Path):
    text = BEATS_YAML.read_text()
    bare = tmp_path / "bare.yaml"
    bare.write_text(re.sub(r"^pace_scale:", "pace_scal:", text, count=1, flags=re.M))
    with pytest.raises(AssertionError):
        abs_band.load_pace(bare)
    no_targets = tmp_path / "none.yaml"
    no_targets.write_text(text.replace("\nbeats:\n", "\nbeatz:\n", 1))
    with pytest.raises(AssertionError):
        abs_band.load_pace(no_targets)


def test_a_route_that_reaches_nothing_says_so():
    line = abs_band.summary("typical", abs_band.reached({"B4": 3 * DAY}, 0, PACE), PACE)
    assert abs_band.NONE_REACHED in line
    assert abs_band.NONE_REACHED not in abs_band.summary("typical", {BEAT: D * S - 0.5}, PACE)
