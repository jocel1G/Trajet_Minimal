import pytest

from src.domain.costs import calculate_segment_cost
from src.domain.errors import UnsupportedConfigurationError
from src.domain.models import CostCriterion, RouteSegment


def test_criteria_use_their_selected_metric():
    segment = RouteSegment("a", "b", distance=10, duration=2, monetary_cost=7)
    assert calculate_segment_cost(segment, CostCriterion.distance()) == 10
    assert calculate_segment_cost(segment, CostCriterion.duration()) == 2
    assert calculate_segment_cost(segment, CostCriterion.monetary_cost()) == 7


def test_weighted_cost_is_explicit_and_rejects_invalid_weights():
    segment = RouteSegment("a", "b", distance=10, duration=2)
    assert calculate_segment_cost(segment, CostCriterion.weighted({"distance": 0.6, "duration": 0.4})) == pytest.approx(6.8)
    with pytest.raises(UnsupportedConfigurationError):
        calculate_segment_cost(segment, CostCriterion.weighted({"distance": -1}))
