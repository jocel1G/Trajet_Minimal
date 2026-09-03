from src.domain.models import Location
from src.routing.adapters.deterministic import DeterministicRoutingProvider


def test_deterministic_provider_returns_normalized_geometry():
    origin = Location("o", "Origin", 0, 0)
    destination = Location("d", "Destination", 1, 1)
    segment = DeterministicRoutingProvider().get_segment(origin, destination, 1)
    assert segment.is_reachable
    assert segment.geometry == ((0, 0), (1, 1))
    assert segment.provider == "deterministic"
