from src.domain.models import CostCriterion, Journey, Location
from src.domain.optimizer import optimize
from tests.fixtures.routing_fixtures import MatrixRoutingProvider


def test_optimizer_reports_measurement_metadata():
    points = [Location("o", "Origin", 0, 0), Location("d", "Destination", 1, 1)]
    result = optimize(Journey("j", points, "o", "d", CostCriterion.distance()), MatrixRoutingProvider({("o", "d"): (5, 2)}), 1, 10)
    assert result.evaluated_routes == 1
    assert result.provider_requests == 1
    assert result.elapsed_ms >= 0
