class OptimizationError(Exception):
    category = "optimization_failure"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidInputError(OptimizationError):
    category = "invalid_input"


class InvalidCoordinatesError(OptimizationError):
    category = "invalid_coordinates"


class UnreachableLocationError(OptimizationError):
    category = "unreachable_location"


class RoutingProviderError(OptimizationError):
    category = "routing_provider_failure"


class UnsupportedConfigurationError(OptimizationError):
    category = "unsupported_configuration"


class OptimizationTimeoutError(OptimizationError):
    category = "timeout"


class ResourceLimitError(OptimizationError):
    category = "resource_limit"
