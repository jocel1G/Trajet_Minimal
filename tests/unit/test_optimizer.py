import pytest

from src.domain.errors import ResourceLimitError, UnreachableLocationError
from src.domain.models import CostCriterion, Journey, Location
from src.domain.optimizer import optimize
from tests.fixtures.routing_fixtures import MatrixRoutingProvider


def locations():
    return [Location("o", "Origin", 0, 0), Location("a", "A", 1, 1), Location("b", "B", 2, 2), Location("d", "Destination", 3, 3)]


def matrix():
    values = {
        ("o", "a"): (1, 1), ("a", "b"): (1, 1), ("b", "d"): (1, 1),
        ("o", "b"): (8, 8), ("b", "a"): (8, 8), ("a", "d"): (8, 8),
    }
    return values


def test_exact_optimizer_finds_better_order_and_reuses_segments():
    points = locations()
    journey = Journey("j", points, "o", "d", CostCriterion.distance())
    provider = MatrixRoutingProvider(matrix())

    result = optimize(journey, provider, timeout_seconds=1, point_limit=10)

    assert result.ordered_location_ids == ("o", "a", "b", "d")
    assert result.total_cost == 3
    assert result.exactness == "exact"
    assert result.evaluated_routes == 2
    assert len(provider.requests) == 6


def test_optimizer_rejects_unreachable_route_and_resource_limit():
    points = locations()
    journey = Journey("j", points, "o", "d", CostCriterion.distance())
    with pytest.raises(UnreachableLocationError):
        optimize(journey, MatrixRoutingProvider({}), timeout_seconds=1, point_limit=10)

    with pytest.raises(ResourceLimitError):
        optimize(journey, MatrixRoutingProvider(matrix()), timeout_seconds=1, point_limit=2)
