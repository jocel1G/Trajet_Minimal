from src.application.optimize_journey import OptimizeJourney
from src.domain.models import CostCriterion, Journey, Location
from tests.fixtures.routing_fixtures import MatrixRoutingProvider


def test_optimize_use_case_returns_explainable_exact_result():
    points = [Location("o", "Origin", 0, 0), Location("a", "A", 1, 1), Location("d", "Destination", 2, 2)]
    journey = Journey("journey-1", points, "o", "d", CostCriterion.distance())
    provider = MatrixRoutingProvider({("o", "a"): (2, 3), ("a", "d"): (2, 3), ("o", "d"): (9, 9)})

    result = OptimizeJourney(provider, point_limit=10).execute(journey)

    assert result.ordered_location_ids == ("o", "a", "d")
    assert result.total_distance == 4
    assert result.provider == "fixture"
    assert result.algorithm == "exhaustive_permutation"
