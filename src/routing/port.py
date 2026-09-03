from typing import Protocol

from src.domain.models import Location, RouteSegment


class RoutingProvider(Protocol):
    name: str

    def get_segment(self, origin: Location, destination: Location, timeout_seconds: float) -> RouteSegment:
        """Return normalized directional route data."""
