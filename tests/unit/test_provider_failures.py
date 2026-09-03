import pytest

from src.application.optimize_journey import OptimizeJourney
from src.domain.errors import OptimizationTimeoutError, RoutingProviderError
from src.domain.models import CostCriterion, Journey, Location


class TimeoutProvider:
    name = "timeout"

    def get_segment(self, origin, destination, timeout_seconds):
        raise TimeoutError("provider timeout")


class DownProvider:
    name = "down"

    def get_segment(self, origin, destination, timeout_seconds):
        raise ConnectionError("provider unavailable")


def make_journey():
    points = [Location("o", "Origin", 0, 0), Location("d", "Destination", 1, 1)]
    return Journey("j", points, "o", "d", CostCriterion.distance())


def test_provider_exceptions_are_categorized():
    with pytest.raises(OptimizationTimeoutError):
        OptimizeJourney(TimeoutProvider()).execute(make_journey())
    with pytest.raises(RoutingProviderError):
        OptimizeJourney(DownProvider()).execute(make_journey())
