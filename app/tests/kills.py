"""The `@kills(row, ...)` marker of a suite whose tests sit outside tests/engine_contract: the rows of the suite's
MUTANTS_*.txt the test must turn red for (tools/mutate_suite.py reads it off the source)."""
import pytest


def kills(*rows: int) -> pytest.MarkDecorator:
    return pytest.mark.kills(*rows)
