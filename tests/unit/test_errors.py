from src.domain.errors import (
    InvalidCoordinatesError,
    OptimizationError,
    ResourceLimitError,
    RoutingProviderError,
)


def test_errors_expose_stable_categories():
    assert InvalidCoordinatesError("bad").category == "invalid_coordinates"
    assert RoutingProviderError("down").category == "routing_provider_failure"
    assert ResourceLimitError("too many").category == "resource_limit"
    assert isinstance(OptimizationError("failed"), Exception)
