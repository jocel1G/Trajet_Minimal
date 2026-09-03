# Quickstart Validation: Multi-Point Ride Optimizer

This guide validates the feature from the desktop workflow through route persistence. It is a
validation contract, not an implementation guide.

## Prerequisites

- Python 3.11 or newer with Tkinter available.
- Docker Desktop with Docker Compose.
- A checkout of the repository at the feature implementation.
- A deterministic routing fixture or configured routing source for the scenarios below.

## Setup

1. Create and activate a Python virtual environment.
2. Install the project dependencies from `requirements.txt`.
3. Start the SQLite data service and mounted volume:

   ```text
   docker compose -f docker/docker-compose.yml up -d
   ```

4. Confirm that the configured SQLite file is available through the host-mounted `data/` directory.
5. Start the desktop application with the project entry point documented by the implementation.

## Scenario 1: Manage Journey Points

1. Add an origin, destination, and at least three intermediate points with valid coordinates.
2. Modify one point's label or coordinates and confirm the list and map marker update.
3. Delete an unused point and confirm it disappears from the list and map.
4. Attempt to delete a point referenced by a saved journey and confirm the application explains why it
   cannot be deleted.
5. Close and reopen the application and confirm the saved points remain available.

Expected outcome: point management is reflected consistently in the list, map, and SQLite-backed
state.

## Scenario 2: Optimize and Display a Route

1. Select distance as the cost criterion.
2. Submit a journey whose optimal intermediate order differs from the input order.
3. Confirm the origin is first, the destination is last, every required point appears exactly once,
   and the reported distance is minimal for the fixture.
4. Select a different criterion or explicit weighted combination and repeat the optimization.
5. Confirm the result reports the criterion, weights when applicable, total cost, route metrics,
   exactness status, and route-source/algorithm metadata.
6. Confirm the selected route and available geometry are drawn on the map.
7. Close and reopen the application and confirm the saved optimal route can be viewed.

Expected outcome: the user can compare and understand a valid optimized route without relying on
input order.

## Scenario 3: Failure and Boundary Handling

Run the following cases independently:

- Empty, one-point, and two-point journeys.
- Duplicate points.
- Missing or out-of-range coordinates.
- An unreachable location.
- A missing metric for the selected criterion.
- A journey above the exact-optimization limit.
- A route-source timeout or unavailable source.

Expected outcome: each case either produces the defined valid boundary result or a categorized,
user-readable error. The application does not freeze, crash, or label an approximate/unverified route
as exact optimal output.

## Automated Validation

Run the project's test command after implementation:

```text
pytest
```

The test suite must include independent optimizer tests, routing-adapter tests with deterministic
fixtures, persistence tests against a temporary SQLite database, and use-case tests covering the
primary journeys. Contract details are defined in [`contracts/`](contracts/) and the entity rules in
[`data-model.md`](data-model.md).

## Teardown

```text
docker compose -f docker/docker-compose.yml down
```

Keep the mounted database volume when validating persistence across runs. Remove it only when a clean
state is intentionally required.
