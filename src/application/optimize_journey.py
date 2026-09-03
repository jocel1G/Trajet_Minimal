from src.domain.errors import (
    OptimizationError,
    OptimizationTimeoutError,
    RoutingProviderError,
)
from src.domain.optimizer import optimize


class OptimizeJourney:
    def __init__(self, provider, point_limit: int = 10, timeout_seconds: float = 10.0):
        self.provider = provider
        self.point_limit = point_limit
        self.timeout_seconds = timeout_seconds

    def execute(self, journey):
        try:
            return optimize(journey, self.provider, self.timeout_seconds, self.point_limit)
        except OptimizationError:
            raise
        except TimeoutError as error:
            raise OptimizationTimeoutError("Routing provider timed out") from error
        except (ConnectionError, OSError) as error:
            raise RoutingProviderError("Routing provider is unavailable") from error
