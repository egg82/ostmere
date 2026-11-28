"""The content files the loader reads, in order (schema.load_opening): the opening, each chapter after it, and the chapters
still in writing. Paths only; schema.py re-exports every name."""
from pathlib import Path

OPENING = Path(__file__).resolve().parent / "opening.toml"
DAY_ONE = Path(__file__).resolve().parent / "days" / "day_one.toml"
DAY_TWO = Path(__file__).resolve().parent / "days" / "day_two.toml"
DAY_THREE = Path(__file__).resolve().parent / "days" / "day_three.toml"
DAY_FOUR = Path(__file__).resolve().parent / "days" / "day_four.toml"
DAY_FIVE = Path(__file__).resolve().parent / "days" / "day_five.toml"
B7 = Path(__file__).resolve().parent / "days" / "b7.toml"
DAY_SIX = Path(__file__).resolve().parent / "days" / "day_six.toml"
DAY_EIGHT = Path(__file__).resolve().parent / "days" / "day_eight.toml"
DAY_NINE = Path(__file__).resolve().parent / "days" / "day_nine.toml"
DAY_ELEVEN = Path(__file__).resolve().parent / "days" / "day_eleven.toml"
DAY_TWELVE = Path(__file__).resolve().parent / "days" / "day_twelve.toml"
DAY_FIFTEEN = Path(__file__).resolve().parent / "days" / "day_fifteen.toml"
DAY_SIXTEEN = Path(__file__).resolve().parent / "days" / "day_sixteen.toml"
DAY_EIGHTEEN = Path(__file__).resolve().parent / "days" / "day_eighteen.toml"
DAY_NINETEEN = Path(__file__).resolve().parent / "days" / "day_nineteen.toml"
DAY_TWENTY_TWO = Path(__file__).resolve().parent / "days" / "day_twenty_two.toml"
DAY_TWENTY_THREE = Path(__file__).resolve().parent / "days" / "day_twenty_three.toml"
DAY_TWENTY_FIVE = Path(__file__).resolve().parent / "days" / "day_twenty_five.toml"
DAY_TWENTY_SEVEN = Path(__file__).resolve().parent / "days" / "day_twenty_seven.toml"
DAY_TWENTY_NINE = Path(__file__).resolve().parent / "days" / "day_twenty_nine.toml"
DAY_THIRTY = Path(__file__).resolve().parent / "days" / "day_thirty.toml"
PRESTIGE = Path(__file__).resolve().parent / "prestige.toml"
PHASE_PAYS = Path(__file__).resolve().parent / "phase_pays.toml"
CHAPTERS = (DAY_ONE, DAY_TWO, DAY_THREE, DAY_FOUR, DAY_FIVE, B7, DAY_SIX, DAY_EIGHT, DAY_NINE, DAY_ELEVEN,
            DAY_TWELVE, DAY_FIFTEEN, DAY_SIXTEEN, DAY_EIGHTEEN, DAY_NINETEEN, DAY_TWENTY_TWO,
            DAY_TWENTY_THREE, DAY_TWENTY_FIVE, DAY_TWENTY_SEVEN, DAY_TWENTY_NINE, DAY_THIRTY, PRESTIGE, PHASE_PAYS)
"""The chapters after the opening, merged on in this order (Chapter): what ships. Prestige and its phase pays come
last, since the phase pays expand over every skill row the chapters before them wrote."""
IN_WRITING: tuple[Path, ...] = ()
"""Chapters whose structure is in but whose lines are not, merged after CHAPTERS only by tests; each moves into
CHAPTERS once no text of it is UNWRITTEN (tests/rules/content/test_day_two.py) and its pacing holds."""
UNWRITTEN = "[day two: line to write]"
"""The text of a key whose line is still to write; no shipping release holds it."""
