"""tools/play_report.py on a small fixture of the log lines the app writes."""
from pathlib import Path

from tools.play_report import build_chains, parse, report

FIXTURE = Path(__file__).parent / "fixtures" / "play.log"


def test_parse_reads_a_line_and_skips_noise():
    got = parse(FIXTURE.read_text().splitlines()[1])
    assert got["event"] == "game.request" and got["target"] == "gather" and got["gap_s"] == "5" and got["save"] == "11"
    assert parse("not a log line") == {}


def test_two_saves_are_two_games_with_their_gaps_and_failures():
    first, second = build_chains([f for f in map(parse, FIXTURE.read_text().splitlines()) if f])
    assert (first.steps, first.last_at, first.longest_gap, first.gap_step, first.gap_target) == (3, 120, 45, 2, "build")
    assert dict(first.failed) == {"build": 2} and first.errors == 1
    assert (second.steps, second.last_at, second.longest_gap) == (1, 0, 18)


def test_report_names_where_players_left_and_time_to_the_end():
    text = report(FIXTURE.read_text().splitlines())
    assert "2 leaves" in text and "2 client errors" not in text
    assert "game 1: 3 decisions" in text and "failed taps: build x2" in text
    assert "left before the end after 88s" in text and "reached the end after 300s" in text
    assert "[300]" in text


def _taps(*cards: str) -> list[str]:
    """One decision on save 5 per entry: a card id is a tap on it, "-" is a switch_mix (a decision that is not a tap)."""
    return [
        f"ts=2026-10-16T10:00:{i:02d}.000Z level=info event=game.request route=/api/saves/{{save_id}}/decisions save=5 "
        f"decision={'switch_mix' if card == '-' else 'tap_card'}{'' if card == '-' else f' target={card}'} "
        f"after={i} status=200 ms=3 wall_s={i} gap_s=1 failed=0"
        for i, card in enumerate(cards)]


def test_runs_of_one_card_tapped_in_a_row_are_counted_per_game():
    lines = _taps(*["scavenge"] * 6, "gather", "scavenge", "scavenge", "-", "scavenge", *["gather"] * 5)
    (chain,) = build_chains([f for f in map(parse, lines) if f])
    assert chain.runs == [6, 1, 2, 1, 5]   # the switch ends the run of scavenge
    assert "longest run of one card tapped 6, runs of 5+ 2" in report(lines)
