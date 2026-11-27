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
               "tests/rules/loaders/test_leaves_loader.py", "tests/rules/loaders/test_retired_chores_loader.py")
SUITES = {
    "held": Suite("MUTANTS_held.txt", "test_held_*.py", "mutants/held", home=f"{CONTRACT}/held"),
    "drains": Suite("MUTANTS_drains.txt", "test_drains_*.py", "mutants/drains", home=f"{CONTRACT}/drains"),
    "spent": Suite("MUTANTS_spent.txt", "test_spent_*.py", "mutants/spent", home=f"{CONTRACT}/spent"),
    "heldspeed": Suite("MUTANTS_heldspeed.txt", "test_heldspeed_*.py", "mutants/heldspeed", home=f"{CONTRACT}/heldspeed"),
    "share": Suite("MUTANTS_share.txt", "test_share_levels_*.py", "mutants/share", home=f"{CONTRACT}/leaves"),
    "guards": Suite("MUTANTS_guards.txt", "test_guards_*.py", "mutants/guards", home=f"{CONTRACT}/guards"),
    "or_else": Suite("MUTANTS_or_else.txt", "test_or_else_*_contract.py", "mutants/or_else", home=f"{CONTRACT}/guards"),
    "groups": Suite("MUTANTS_groups.txt", "test_groups_*_contract.py", "mutants/groups", home=f"{CONTRACT}/groups"),
    "leaves": Suite("MUTANTS_leaves.txt", "test_leaves_*.py", "mutants/leaves", 1, 20,
                    ("tests/engine_contract/leaves/test_retire_*.py", *LEAVES_ALSO), home=f"{CONTRACT}/leaves"),
    "retire": Suite("MUTANTS_leaves.txt", "test_retire_*.py", "mutants/retire", 21, 33,
                    ("tests/engine_contract/leaves/test_leaves_*.py", *LEAVES_ALSO), home=f"{CONTRACT}/leaves"),
    "casting": Suite("MUTANTS.txt", "test_casting_*_contract.py", "mutants/casting", home=f"{CONTRACT}/casting"),
    "spells": Suite("MUTANTS.txt", "test_spells_*_contract.py", "mutants/spells", home=f"{CONTRACT}/spells"),
    "clocks": Suite("MUTANTS_clocks.txt", "test_failover.py", "mutants/clocks", also=(
        "tests/db/test_prune_race.py", "tests/db/test_reminders.py", "tests/db/test_hands_free.py",
        "tests/reminders/test_sender.py", "tests/dayone/engine/test_dayone_forecast.py"), home="tests/db"),
    "journal_days": Suite("MUTANTS_journal_days.txt", "test_journal_days.py", "mutants/journal_days", also=(
        "tests/saves/journal/test_journal_*.py", "tests/db/stored/test_journal_*.py", "tests/db/stored/test_decision_lock_span.py",
        "tests/db/stored/test_save_journal_migrate.py", "tests/api/test_journal_days_wire.py"), home="tests/saves/journal"),
    "queue": Suite("MUTANTS_queue.txt", "test_queue.py", "mutants/queue", home="tests/writer"),
    "live": Suite("MUTANTS_live.txt", "test_live.py", "mutants/live", home="tests/writer"),
}
