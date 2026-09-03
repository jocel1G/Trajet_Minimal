import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = "data/ride_optimizer.sqlite3"
    exact_point_limit: int = 10
    provider_timeout_seconds: float = 10.0
    routing_provider: str = "deterministic"

    @classmethod
    def from_environment(cls):
        return cls(
            db_path=os.getenv("RIDE_OPTIMIZER_DB_PATH", cls.db_path),
            exact_point_limit=int(os.getenv("RIDE_OPTIMIZER_EXACT_POINT_LIMIT", cls.exact_point_limit)),
            provider_timeout_seconds=float(os.getenv("RIDE_OPTIMIZER_PROVIDER_TIMEOUT_SECONDS", cls.provider_timeout_seconds)),
            routing_provider=os.getenv("RIDE_OPTIMIZER_ROUTING_PROVIDER", cls.routing_provider),
        )
