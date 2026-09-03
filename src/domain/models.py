from dataclasses import dataclass, field
from typing import Literal

from .errors import InvalidCoordinatesError, InvalidInputError, UnsupportedConfigurationError

MetricName = Literal["distance", "duration", "monetary_cost"]
SegmentStatus = Literal["reachable", "unreachable", "provider_error", "missing_metric"]


@dataclass(frozen=True)
class Location:
    id: str
    label: str
    latitude: float
    longitude: float

    def __post_init__(self):
        if not self.label.strip():
            raise InvalidInputError("Location label cannot be empty")
        if not -90 <= self.latitude <= 90 or not -180 <= self.longitude <= 180:
            raise InvalidCoordinatesError(f"Invalid coordinates for {self.id}")


@dataclass(frozen=True)
class CostCriterion:
    kind: str
    weights: dict[str, float] = field(default_factory=dict)

    @classmethod
    def distance(cls):
        return cls("distance")

    @classmethod
    def duration(cls):
        return cls("duration")

    @classmethod
    def monetary_cost(cls):
        return cls("monetary_cost")

    @classmethod
    def weighted(cls, weights: dict[str, float]):
        return cls("weighted", dict(weights))


@dataclass(frozen=True)
class Journey:
    id: str
    locations: tuple[Location, ...] | list[Location]
    origin_id: str
    destination_id: str | None
    cost_criterion: CostCriterion
    visit_policy: str = "each_intermediate_once"
    status: str = "draft"

    def __post_init__(self):
        object.__setattr__(self, "locations", tuple(self.locations))
        location_ids = [location.id for location in self.locations]
        if self.origin_id not in location_ids:
            raise InvalidInputError("Origin must belong to journey locations")
        if self.destination_id is not None:
            if self.destination_id not in location_ids:
                raise InvalidInputError("Destination must belong to journey locations")
            if self.destination_id == self.origin_id:
                raise InvalidInputError("Origin and destination must differ")

    @property
    def intermediate_locations(self):
        excluded = {self.origin_id, self.destination_id}
        return tuple(location for location in self.locations if location.id not in excluded)


@dataclass(frozen=True)
class RouteSegment:
    from_location_id: str
    to_location_id: str
    status: SegmentStatus = "reachable"
    distance: float | None = None
    duration: float | None = None
    monetary_cost: float | None = None
    geometry: tuple[tuple[float, float], ...] = ()
    provider: str = "unknown"

    @property
    def is_reachable(self):
        return self.status == "reachable"


@dataclass(frozen=True)
class OptimizationResult:
    journey_id: str
    ordered_location_ids: tuple[str, ...]
    total_cost: float
    criterion: CostCriterion
    total_distance: float | None = None
    total_duration: float | None = None
    total_monetary_cost: float | None = None
    exactness: str = "exact"
    algorithm: str = "exhaustive_permutation"
    provider: str = "unknown"
    evaluated_routes: int = 0
    provider_requests: int = 0
    elapsed_ms: float = 0
    geometry: tuple[tuple[float, float], ...] = ()


def criterion_from_dict(data: dict) -> CostCriterion:
    kind = data.get("kind")
    if kind == "distance":
        return CostCriterion.distance()
    if kind == "duration":
        return CostCriterion.duration()
    if kind == "monetary_cost":
        return CostCriterion.monetary_cost()
    if kind == "weighted":
        return CostCriterion.weighted(data.get("weights", {}))
    raise UnsupportedConfigurationError("Unsupported cost criterion")
