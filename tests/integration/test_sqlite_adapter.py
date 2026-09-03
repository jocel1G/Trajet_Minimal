import pytest

from src.domain.models import CostCriterion, Journey, Location
from src.persistence.sqlite_adapter import SQLitePersistence


def test_sqlite_persists_order_and_protects_referenced_locations(tmp_path):
    store = SQLitePersistence(tmp_path / "ride.sqlite3")
    origin = Location("o", "Origin", 0, 0)
    stop = Location("s", "Stop", 1, 1)
    destination = Location("d", "Destination", 2, 2)
    for location in (origin, stop, destination):
        store.save_location(location)

    journey = Journey("j", [origin, stop, destination], origin.id, destination.id, CostCriterion.distance())
    store.save_journey(journey)
    loaded = store.get_journey("j")
    assert [location.id for location in loaded.locations] == ["o", "s", "d"]

    assert store.delete_location("s") is True
    with pytest.raises(KeyError):
        store.get_journey("j")
