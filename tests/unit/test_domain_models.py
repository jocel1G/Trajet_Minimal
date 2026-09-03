import pytest

from src.domain.errors import InvalidCoordinatesError, InvalidInputError
from src.domain.models import CostCriterion, Journey, Location, RouteSegment


def test_location_validates_coordinates():
    location = Location("a", "A", 48.8566, 2.3522)
    assert location.label == "A"

    with pytest.raises(InvalidCoordinatesError):
        Location("bad", "Bad", 91, 2)


def test_journey_requires_distinct_endpoints_and_membership():
    origin = Location("o", "Origin", 0, 0)
    destination = Location("d", "Destination", 1, 1)
    journey = Journey("j", [origin, destination], origin.id, destination.id, CostCriterion.distance())
    assert journey.intermediate_locations == ()

    with pytest.raises(InvalidInputError):
        Journey("bad", [origin], "missing", None, CostCriterion.distance())


def test_route_segment_distinguishes_failure_statuses():
    segment = RouteSegment("a", "b", status="provider_error")
    assert not segment.is_reachable
    assert segment.status == "provider_error"
