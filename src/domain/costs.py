from .errors import UnsupportedConfigurationError
from .models import CostCriterion, RouteSegment


def validate_criterion(criterion: CostCriterion) -> None:
    if criterion.kind in {"distance", "duration", "monetary_cost"}:
        return
    if criterion.kind != "weighted" or not criterion.weights:
        raise UnsupportedConfigurationError("A cost criterion is required")
    if any(value < 0 for value in criterion.weights.values()):
        raise UnsupportedConfigurationError("Cost weights cannot be negative")
    if not any(value > 0 for value in criterion.weights.values()):
        raise UnsupportedConfigurationError("At least one cost weight must be positive")
    supported = {"distance", "duration", "monetary_cost"}
    if set(criterion.weights) - supported:
        raise UnsupportedConfigurationError("Weighted criterion contains an unsupported metric")


def calculate_segment_cost(segment: RouteSegment, criterion: CostCriterion) -> float:
    validate_criterion(criterion)
    values = {
        "distance": segment.distance,
        "duration": segment.duration,
        "monetary_cost": segment.monetary_cost,
    }
    if not segment.is_reachable:
        raise UnsupportedConfigurationError(f"Segment is not reachable: {segment.status}")
    if criterion.kind != "weighted":
        value = values[criterion.kind]
        if value is None:
            raise UnsupportedConfigurationError(f"Missing {criterion.kind} metric")
        return float(value)
    total = 0.0
    for metric, weight in criterion.weights.items():
        value = values[metric]
        if value is None:
            raise UnsupportedConfigurationError(f"Missing {metric} metric")
        total += weight * value
    return total
