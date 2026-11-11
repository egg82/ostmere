"""One logfmt line per lesson end a save newly holds (SavePresentation.lesson_ends): ids, counts and seconds only."""
import logging
from collections.abc import Iterable

from .. import logs
from .saves_models import LessonEnd

_log = logging.getLogger("ashfall.game")


def log_new_ends(save_id: int, before: Iterable[LessonEnd], after: Iterable[LessonEnd]) -> None:
    seen = {e.lesson for e in before}
    for end in after:
        if end.lesson not in seen:
            seen.add(end.lesson)
            logs.info(_log, "lesson.end", save=save_id, lesson=end.lesson, outcome="skipped" if end.skipped else "done", step=end.step,
                      longest_wait_s=end.longest_wait_s)
