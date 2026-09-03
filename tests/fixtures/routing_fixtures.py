from src.domain.models import Location, RouteSegment
from src.routing.port import RoutingProvider


class MatrixRoutingProvider(RoutingProvider):
    name = "fixture"

    def __init__(self, matrix):
        self.matrix = matrix
        self.requests = []

    def get_segment(self, origin, destination, timeout_seconds):
        self.requests.append((origin.id, destination.id))
        value = self.matrix.get((origin.id, destination.id))
        if value is None:
            return RouteSegment(origin.id, destination.id, status="unreachable")
        distance, duration = value
        return RouteSegment(origin.id, destination.id, distance=distance, duration=duration)
