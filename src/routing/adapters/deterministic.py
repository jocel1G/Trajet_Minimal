from src.domain.models import Location, RouteSegment


class DeterministicRoutingProvider:
    name = "deterministic"

    def get_segment(self, origin: Location, destination: Location, timeout_seconds: float) -> RouteSegment:
        distance = ((origin.latitude - destination.latitude) ** 2 + (origin.longitude - destination.longitude) ** 2) ** 0.5
        geometry = ((origin.latitude, origin.longitude), (destination.latitude, destination.longitude))
        return RouteSegment(origin.id, destination.id, distance=distance, duration=distance, monetary_cost=distance, geometry=geometry, provider=self.name)
