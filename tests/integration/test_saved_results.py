from src.application.journey_persistence import JourneyPersistence
from src.domain.models import CostCriterion, Journey, Location, OptimizationResult
from src.persistence.sqlite_adapter import SQLitePersistence


def test_saved_journey_and_result_round_trip(tmp_path):
    store = SQLitePersistence(tmp_path / "saved.sqlite3")
    persistence = JourneyPersistence(store)
    points = [Location("o", "Origin", 0, 0), Location("d", "Destination", 1, 1)]
    journey = Journey("journey", points, "o", "d", CostCriterion.distance())
    result = OptimizationResult("journey", ("o", "d"), 2, CostCriterion.distance(), total_distance=2, geometry=((0, 0), (1, 1)))

    persistence.save_journey(journey)
    persistence.save_result(result)

    assert [item.id for item in persistence.load_journey("journey").locations] == ["o", "d"]
    loaded = persistence.load_result("journey-result")
    assert loaded.ordered_location_ids == ("o", "d")
    assert loaded.geometry == ((0, 0), (1, 1))


def test_saved_journeys_can_be_listed_for_loading(tmp_path):
    store = SQLitePersistence(tmp_path / "journeys.sqlite3")
    points = [Location("o", "Origin", 0, 0), Location("d", "Destination", 1, 1)]
    for point in points:
        store.save_location(point)
    store.save_journey(Journey("journey", points, "o", "d", CostCriterion.distance()))

    journeys = store.list_journeys()

    assert [journey.id for journey in journeys] == ["journey"]
