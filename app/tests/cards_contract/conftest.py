"""Hypothesis profiles for the cards contract suite. Default `contract` keeps the whole suite under ~2 minutes on
1-2 CPUs; the nightly deep run uses HYPOTHESIS_PROFILE=ci (200 examples), with the per-test ceiling and timeout raised for it."""
import os
from typing import cast

from hypothesis import HealthCheck, Phase, settings

_COMMON = settings(
    deadline=None, database=None,
    suppress_health_check=cast(list[HealthCheck], list(HealthCheck)),  # stubs -- iterating HealthCheck yields its metaclass
)
_NO_SHRINK = (Phase.explicit, Phase.reuse, Phase.generate)
# Default: fast and derandomized, so a push's gate cannot flake (the random search is the nightly `ci` profile).
# Shrinking is off (a failing run otherwise spends minutes minimising); `debug` turns it back on.
settings.register_profile("contract", _COMMON, max_examples=20, phases=_NO_SHRINK, derandomize=True)
settings.register_profile("ci", _COMMON, max_examples=200, phases=_NO_SHRINK)
settings.register_profile("debug", _COMMON, max_examples=50)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "contract"))
