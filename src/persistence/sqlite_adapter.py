import json
import sqlite3
from pathlib import Path

from src.domain.models import CostCriterion, Journey, Location, OptimizationResult, criterion_from_dict


class SQLitePersistence:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def _initialize(self):
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY, label TEXT NOT NULL, latitude REAL NOT NULL,
                longitude REAL NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS journeys (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, origin_id TEXT NOT NULL,
                destination_id TEXT, visit_policy TEXT NOT NULL, criterion_json TEXT NOT NULL,
                status TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(origin_id) REFERENCES locations(id),
                FOREIGN KEY(destination_id) REFERENCES locations(id)
            );
            CREATE TABLE IF NOT EXISTS journey_locations (
                journey_id TEXT NOT NULL, location_id TEXT NOT NULL, position INTEGER NOT NULL,
                PRIMARY KEY(journey_id, position),
                FOREIGN KEY(journey_id) REFERENCES journeys(id) ON DELETE CASCADE,
                FOREIGN KEY(location_id) REFERENCES locations(id)
            );
            CREATE TABLE IF NOT EXISTS optimization_results (
                id TEXT PRIMARY KEY, journey_id TEXT NOT NULL, total_cost REAL NOT NULL,
                criterion_json TEXT NOT NULL, total_distance REAL, total_duration REAL,
                total_monetary_cost REAL, exactness TEXT NOT NULL, algorithm TEXT NOT NULL,
                provider TEXT NOT NULL, evaluated_routes INTEGER NOT NULL,
                provider_requests INTEGER NOT NULL, elapsed_ms REAL NOT NULL,
                geometry_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(journey_id) REFERENCES journeys(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS result_locations (
                result_id TEXT NOT NULL, location_id TEXT NOT NULL, position INTEGER NOT NULL,
                PRIMARY KEY(result_id, position),
                FOREIGN KEY(result_id) REFERENCES optimization_results(id) ON DELETE CASCADE,
                FOREIGN KEY(location_id) REFERENCES locations(id)
            );
            PRAGMA user_version = 1;
            """
        )
        self.connection.commit()

    @staticmethod
    def _criterion_json(criterion: CostCriterion) -> str:
        return json.dumps({"kind": criterion.kind, "weights": criterion.weights}, sort_keys=True)

    def save_location(self, location: Location) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO locations(id, label, latitude, longitude, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (location.id, location.label, location.latitude, location.longitude),
        )
        self.connection.commit()

    def get_location(self, location_id: str) -> Location:
        row = self.connection.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()
        if row is None:
            raise KeyError(location_id)
        return Location(row["id"], row["label"], row["latitude"], row["longitude"])

    def list_locations(self) -> list[Location]:
        rows = self.connection.execute("SELECT * FROM locations ORDER BY created_at, id").fetchall()
        return [Location(row["id"], row["label"], row["latitude"], row["longitude"]) for row in rows]

    def delete_location(self, location_id: str) -> bool:
        with self.connection:
            journey_ids = [
                row["id"]
                for row in self.connection.execute(
                    "SELECT DISTINCT j.id FROM journeys j LEFT JOIN journey_locations jl ON jl.journey_id = j.id WHERE j.origin_id = ? OR j.destination_id = ? OR jl.location_id = ?",
                    (location_id, location_id, location_id),
                ).fetchall()
            ]
            for journey_id in journey_ids:
                self.connection.execute(
                    "DELETE FROM result_locations WHERE result_id IN (SELECT id FROM optimization_results WHERE journey_id = ?)",
                    (journey_id,),
                )
                self.connection.execute(
                    "DELETE FROM optimization_results WHERE journey_id = ?", (journey_id,)
                )
                self.connection.execute(
                    "DELETE FROM journey_locations WHERE journey_id = ?", (journey_id,)
                )
                self.connection.execute("DELETE FROM journeys WHERE id = ?", (journey_id,))
            cursor = self.connection.execute("DELETE FROM locations WHERE id = ?", (location_id,))
            return cursor.rowcount > 0

    def save_journey(self, journey: Journey) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT OR REPLACE INTO journeys(id, name, origin_id, destination_id, visit_policy, criterion_json, status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (journey.id, journey.id, journey.origin_id, journey.destination_id, journey.visit_policy, self._criterion_json(journey.cost_criterion), journey.status),
            )
            self.connection.execute("DELETE FROM journey_locations WHERE journey_id = ?", (journey.id,))
            self.connection.executemany(
                "INSERT INTO journey_locations(journey_id, location_id, position) VALUES (?, ?, ?)",
                [(journey.id, location.id, position) for position, location in enumerate(journey.locations)],
            )

    def get_journey(self, journey_id: str) -> Journey:
        row = self.connection.execute("SELECT * FROM journeys WHERE id = ?", (journey_id,)).fetchone()
        if row is None:
            raise KeyError(journey_id)
        locations = self.connection.execute(
            "SELECT l.* FROM locations l JOIN journey_locations jl ON jl.location_id = l.id WHERE jl.journey_id = ? ORDER BY jl.position",
            (journey_id,),
        ).fetchall()
        return Journey(
            row["id"],
            [Location(item["id"], item["label"], item["latitude"], item["longitude"]) for item in locations],
            row["origin_id"],
            row["destination_id"],
            criterion_from_dict(json.loads(row["criterion_json"])),
            row["visit_policy"],
            row["status"],
        )

    def list_journeys(self) -> list[Journey]:
        rows = self.connection.execute(
            "SELECT id FROM journeys ORDER BY updated_at DESC, id"
        ).fetchall()
        return [self.get_journey(row["id"]) for row in rows]

    def save_result(self, result: OptimizationResult) -> None:
        result_id = getattr(result, "id", None) or f"{result.journey_id}-result"
        with self.connection:
            self.connection.execute(
                "INSERT OR REPLACE INTO optimization_results(id, journey_id, total_cost, criterion_json, total_distance, total_duration, total_monetary_cost, exactness, algorithm, provider, evaluated_routes, provider_requests, elapsed_ms, geometry_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (result_id, result.journey_id, result.total_cost, self._criterion_json(result.criterion), result.total_distance, result.total_duration, result.total_monetary_cost, result.exactness, result.algorithm, result.provider, result.evaluated_routes, result.provider_requests, result.elapsed_ms, json.dumps(result.geometry)),
            )
            self.connection.execute("DELETE FROM result_locations WHERE result_id = ?", (result_id,))
            self.connection.executemany(
                "INSERT INTO result_locations(result_id, location_id, position) VALUES (?, ?, ?)",
                [(result_id, location_id, position) for position, location_id in enumerate(result.ordered_location_ids)],
            )

    def get_result(self, result_id: str) -> OptimizationResult:
        row = self.connection.execute(
            "SELECT * FROM optimization_results WHERE id = ?", (result_id,)
        ).fetchone()
        if row is None:
            raise KeyError(result_id)
        locations = self.connection.execute(
            "SELECT location_id FROM result_locations WHERE result_id = ? ORDER BY position",
            (result_id,),
        ).fetchall()
        return OptimizationResult(
            journey_id=row["journey_id"],
            ordered_location_ids=tuple(item["location_id"] for item in locations),
            total_cost=row["total_cost"],
            criterion=criterion_from_dict(json.loads(row["criterion_json"])),
            total_distance=row["total_distance"],
            total_duration=row["total_duration"],
            total_monetary_cost=row["total_monetary_cost"],
            exactness=row["exactness"],
            algorithm=row["algorithm"],
            provider=row["provider"],
            evaluated_routes=row["evaluated_routes"],
            provider_requests=row["provider_requests"],
            elapsed_ms=row["elapsed_ms"],
            geometry=tuple(tuple(point) for point in json.loads(row["geometry_json"])),
        )

    def close(self):
        self.connection.close()
