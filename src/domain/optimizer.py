import itertools
import time

from .costs import calculate_segment_cost
from .errors import (
    InvalidInputError,
    ResourceLimitError,
    RoutingProviderError,
    UnreachableLocationError,
    UnsupportedConfigurationError,
)
from .models import Journey, OptimizationResult, RouteSegment


def optimize(journey: Journey, provider, timeout_seconds: float, point_limit: int) -> OptimizationResult:
    if len(journey.locations) > point_limit:
        raise ResourceLimitError(f"Journey has more than {point_limit} points")
    if len({location.id for location in journey.locations}) != len(journey.locations):
        raise InvalidInputError("Journey locations must have unique identifiers")

    start = time.perf_counter()
    origin = next(location for location in journey.locations if location.id == journey.origin_id)
    destination = next((location for location in journey.locations if location.id == journey.destination_id), None)
    intermediates = [location for location in journey.locations if location.id not in {journey.origin_id, journey.destination_id}]
    candidates = itertools.permutations(intermediates)
    cache: dict[tuple[str, str], RouteSegment] = {}
    best_route = None
    best_metrics = None
    evaluated = 0

    def segment_for(left, right):
        key = (left.id, right.id)
        if key not in cache:
            cache[key] = provider.get_segment(left, right, timeout_seconds)
        return cache[key]

    failure_statuses = set()
    for ordering in candidates:
        route = (origin, *ordering) if destination is None else (origin, *ordering, destination)
        segments = [segment_for(left, right) for left, right in zip(route, route[1:])]
        if any(not segment.is_reachable for segment in segments):
            failure_statuses.update(segment.status for segment in segments if not segment.is_reachable)
            continue
        try:
            costs = [calculate_segment_cost(segment, journey.cost_criterion) for segment in segments]
        except Exception:
            raise
        evaluated += 1
        cost = sum(costs)
        if best_metrics is None or cost < best_metrics["cost"]:
            best_route = route
            best_metrics = {
                "cost": cost,
                "distance": sum(segment.distance or 0 for segment in segments),
                "duration": sum(segment.duration or 0 for segment in segments),
                "monetary_cost": sum(segment.monetary_cost or 0 for segment in segments),
                "geometry": tuple(point for segment in segments for point in segment.geometry),
                "provider": next((segment.provider for segment in segments if segment.provider != "unknown"), getattr(provider, "name", "unknown")),
            }

    if best_route is None:
        if "provider_error" in failure_statuses:
            raise RoutingProviderError("Routing provider failed for a required segment")
        if "missing_metric" in failure_statuses:
            raise UnsupportedConfigurationError("A required route metric is unavailable")
        raise UnreachableLocationError("No reachable route satisfies the journey rules")
    elapsed_ms = (time.perf_counter() - start) * 1000
    return OptimizationResult(
        journey_id=journey.id,
        ordered_location_ids=tuple(location.id for location in best_route),
        total_cost=best_metrics["cost"],
        criterion=journey.cost_criterion,
        total_distance=best_metrics["distance"],
        total_duration=best_metrics["duration"],
        total_monetary_cost=best_metrics["monetary_cost"],
        provider=best_metrics["provider"],
        evaluated_routes=evaluated,
        provider_requests=len(cache),
        elapsed_ms=elapsed_ms,
        geometry=best_metrics["geometry"],
    )
