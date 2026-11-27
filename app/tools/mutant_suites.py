"""The mutant suites: what a suite is and the table of them (read by tools/mutate_suite.py and tools/gates.sh)."""
from dataclasses import dataclass

CONTRACT = "tests/engine_contract"


@dataclass(frozen=True)
class Suite:
    mutants: str
    tests: str
    specs: str
    first: int = 0
    last: int = 10**6
    also: tuple[str, ...] = ()
    """Globs under app/ of test files run with the suite's own, whose claims they do not make."""
    home: str = CONTRACT
    """The directory under app/ holding the suite's MUTANTS file and its own tests."""


LEAVES_ALSO = ("tests/engine/test_leaves_impl.py", "tests/engine/test_retired_chores_impl.py",
               "tests/opening/test_leaves_loader.py", "tests/opening/test_retired_chores_loader.py")
SUITES = {
    "held": Suite("MUTANTS_held.txt", "test_held_*.py", "held_mutants", home=f"{CONTRACT}/held"),
    "drains": Suite("MUTANTS_drains.txt", "test_drains_*.py", "drains_mutants", home=f"{CONTRACT}/drains"),
    "spent": Suite("MUTANTS_spent.txt", "test_spent_*.py", "spent_mutants", home=f"{CONTRACT}/spent"),
    "heldspeed": Suite("MUTANTS_heldspeed.txt", "test_heldspeed_*.py", "heldspeed_mutants", home=f"{CONTRACT}/heldspeed"),
    "share": Suite("MUTANTS_share.txt", "test_share_levels_*.py", "share_mutants", home=f"{CONTRACT}/leaves"),
    "guards": Suite("MUTANTS_guards.txt", "test_guards_*.py", "guards_mutants", home=f"{CONTRACT}/guards"),
    "or_else": Suite("MUTANTS_or_else.txt", "test_or_else_*_contract.py", "or_else_mutants", home=f"{CONTRACT}/guards"),
    "groups": Suite("MUTANTS_groups.txt", "test_groups_*_contract.py", "groups_mutants", home=f"{CONTRACT}/groups"),
    "leaves": Suite("MUTANTS_leaves.txt", "test_leaves_*.py", "leaves_mutants", 1, 20,
                    ("tests/engine_contract/leaves/test_retire_*.py", *LEAVES_ALSO), home=f"{CONTRACT}/leaves"),
    "retire": Suite("MUTANTS_leaves.txt", "test_retire_*.py", "retire_mutants", 21, 33,
                    ("tests/engine_contract/leaves/test_leaves_*.py", *LEAVES_ALSO), home=f"{CONTRACT}/leaves"),
    "clocks": Suite("MUTANTS_clocks.txt", "test_failover.py", "clocks_mutants", also=(
        "tests/db/test_prune_race.py", "tests/db/test_reminders.py", "tests/db/test_hands_free.py",
        "tests/reminders/test_sender.py", "tests/dayone/test_dayone_forecast.py"), home="tests/db"),
    "journal_days": Suite("MUTANTS_journal_days.txt", "test_journal_days.py", "journal_days_mutants", also=(
        "tests/saves/journal/test_journal_*.py", "tests/db/test_journal_*.py", "tests/db/test_decision_lock_span.py",
        "tests/db/test_save_journal_migrate.py", "tests/test_journal_days_wire.py"), home="tests/saves/journal"),
    "queue": Suite("MUTANTS_queue.txt", "test_queue.py", "queue_mutants", home="tests/writer"),
    "live": Suite("MUTANTS_live.txt", "test_live.py", "live_mutants", home="tests/writer"),
}
