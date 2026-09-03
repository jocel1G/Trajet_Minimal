import pytest

from src.application.optimize_journey import OptimizeJourney
from src.domain.errors import UnsupportedConfigurationError
from src.domain.models import CostCriterion, Journey, Location
from tests.fixtures.routing_fixtures import MatrixRoutingProvider


def test_cost_criteria_can_select_different_route_orders():
    points = [Location("o", "Origin", 0, 0), Location("a", "A", 1, 1), Location("b", "B", 2, 2), Location("d", "Destination", 3, 3)]
    matrix = {
        ("o", "a"): (1, 10), ("a", "b"): (1, 10), ("b", "d"): (1, 10),
        ("o", "b"): (4, 1), ("b", "a"): (4, 1), ("a", "d"): (4, 1),
    }
    provider = MatrixRoutingProvider(matrix)
    distance = OptimizeJourney(provider).execute(Journey("distance", points, "o", "d", CostCriterion.distance()))
    duration = OptimizeJourney(provider).execute(Journey("duration", points, "o", "d", CostCriterion.duration()))
    assert distance.criterion.kind == "distance"
    assert duration.criterion.kind == "duration"
    assert distance.ordered_location_ids != duration.ordered_location_ids


def test_invalid_cost_configuration_is_rejected():
    points = [Location("o", "Origin", 0, 0), Location("d", "Destination", 1, 1)]
    journey = Journey("bad", points, "o", "d", CostCriterion.weighted({"distance": 0, "duration": 0}))
    with pytest.raises(UnsupportedConfigurationError):
        OptimizeJourney(MatrixRoutingProvider({("o", "d"): (1, 1)})).execute(journey)
