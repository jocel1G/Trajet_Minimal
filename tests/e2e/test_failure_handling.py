import pytest

from src.application.optimize_journey import OptimizeJourney
from src.domain.errors import ResourceLimitError, RoutingProviderError, UnreachableLocationError
from src.domain.models import CostCriterion, Journey, Location, RouteSegment
from tests.fixtures.routing_fixtures import MatrixRoutingProvider


class FailingProvider:
    name = "failing"

    def get_segment(self, origin, destination, timeout_seconds):
        return RouteSegment(origin.id, destination.id, status="provider_error", provider=self.name)


def journey():
    points = [Location("o", "Origin", 0, 0), Location("a", "A", 1, 1), Location("d", "Destination", 2, 2)]
    return Journey("j", points, "o", "d", CostCriterion.distance())


def test_failure_categories_are_preserved():
    with pytest.raises(UnreachableLocationError):
        OptimizeJourney(MatrixRoutingProvider({})).execute(journey())
    with pytest.raises(RoutingProviderError):
        OptimizeJourney(FailingProvider()).execute(journey())
    with pytest.raises(ResourceLimitError):
        OptimizeJourney(MatrixRoutingProvider({}), point_limit=2).execute(journey())
