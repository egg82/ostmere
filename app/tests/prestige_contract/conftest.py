"""Hypothesis profiles for the prestige contract suite: `contract` is fast and derandomized for pushes, `ci` (200 examples) is the nightly deep run."""
import os

from hypothesis import HealthCheck, Phase, settings

_COMMON = settings(
    deadline=None, database=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.filter_too_much],
)
_NO_SHRINK = (Phase.explicit, Phase.reuse, Phase.generate)
# Default: fast and derandomized, so a push's gate cannot flake (the random search is the nightly `ci` profile).
# Shrinking is off (a failing run otherwise spends minutes minimising); `debug` turns it back on.
settings.register_profile("contract", _COMMON, max_examples=20, phases=_NO_SHRINK, derandomize=True)
settings.register_profile("ci", _COMMON, max_examples=200, phases=_NO_SHRINK)
settings.register_profile("debug", _COMMON, max_examples=50)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "contract"))
