# Multi-Point Ride Optimizer

Desktop Python application for managing journey points and finding an exact lowest-cost route for
small journeys.

## Requirements

- Python 3.11+
- Tkinter installed with Python
- Docker Desktop with Compose

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

docker compose -f docker/docker-compose.yml up -d
python -m src.app
```

Run tests with:

```powershell
pytest
```

The SQLite database is stored at `data/ride_optimizer.sqlite3`, which is mounted into the SQLite
maintenance container. Configure `RIDE_OPTIMIZER_DB_PATH`, `RIDE_OPTIMIZER_EXACT_POINT_LIMIT`,
`RIDE_OPTIMIZER_PROVIDER_TIMEOUT_SECONDS`, and `RIDE_OPTIMIZER_ROUTING_PROVIDER` through the
environment. Provider credentials must be supplied through secure environment configuration.

Journey points and optimization results remain in memory while you edit and optimize. Use the
**Add in database** button to persist the current journey points and the latest optimization result.
Use **Load from database** to open a list of saved journeys, select one, and restore its points and
latest saved optimization result.

The implementation design and validation scenarios are documented in
`specs/001-multi-point-ride-optimizer/`.
