import pytest

from src.domain.costs import calculate_segment_cost, validate_criterion
from src.domain.errors import UnsupportedConfigurationError
from src.domain.models import CostCriterion, RouteSegment


def test_single_metric_costs_are_explicit():
    segment = RouteSegment("a", "b", distance=12, duration=4, monetary_cost=3)
    assert calculate_segment_cost(segment, CostCriterion.distance()) == 12
    assert calculate_segment_cost(segment, CostCriterion.duration()) == 4
    assert calculate_segment_cost(segment, CostCriterion.monetary_cost()) == 3


def test_weighted_cost_requires_positive_weight_and_available_metrics():
    criterion = CostCriterion.weighted({"distance": 0.6, "duration": 0.4})
    segment = RouteSegment("a", "b", distance=10, duration=5)
    assert calculate_segment_cost(segment, criterion) == pytest.approx(8)

    with pytest.raises(UnsupportedConfigurationError):
        validate_criterion(CostCriterion.weighted({"distance": 0, "duration": 0}))

    with pytest.raises(UnsupportedConfigurationError):
        calculate_segment_cost(RouteSegment("a", "b", distance=10), criterion)
