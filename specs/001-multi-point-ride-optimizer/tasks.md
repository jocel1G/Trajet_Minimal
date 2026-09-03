---

description: "Executable task list for the Multi-Point Ride Optimizer"
---

# Tasks: Multi-Point Ride Optimizer

**Input**: Design documents from `/specs/001-multi-point-ride-optimizer/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because the specification explicitly requires unit, integration, and end-to-end
coverage for the optimization domain, routing adapters, persistence, and representative journeys.

**Organization**: Tasks are grouped by user story so each increment can be implemented and tested
independently after the foundational ports and project setup are complete.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python desktop project and its repeatable local execution environment.


- [X] T001 Create the planned Python project directories under `src/`, `tests/`, `docker/`, and `data/`.
- [X] T002 Create `pyproject.toml` with Python 3.11+ metadata, pytest configuration, and source import settings.
- [X] T003 [P] Create `requirements.txt` with `tkintermapview` and pytest dependencies in `requirements.txt`.
- [X] T004 [P] Create `README.md` with local setup, Docker startup, desktop launch, and test commands.
- [X] T005 [P] Create `docker/docker-compose.yml` with the SQLite data volume mounted to `data/`.
- [X] T006 [P] Add `data/.gitkeep` and ignore generated SQLite files in `.gitignore`.

**Purpose**: Build the domain contracts and shared infrastructure required by every user story.

**Critical**: Complete this phase before beginning user-story implementation.

- [X] T007 [P] Define validated Location, Journey, RouteSegment, CostCriterion, OptimizationResult, and OptimizationError models in `src/domain/models.py`.
- [X] T008 [P] Define categorized domain errors for invalid coordinates, unreachable locations, provider failures, unsupported configuration, timeout, and resource limits in `src/domain/errors.py`.
- [X] T009 [P] Implement explicit distance, duration, monetary, and weighted cost calculation with weight validation in `src/domain/costs.py`.
- [X] T010 [P] Define the provider-neutral routing port and normalized segment response in `src/routing/port.py`.
- [X] T011 [P] Define persistence port operations for locations, journeys, and optimization results in `src/persistence/port.py`.
- [X] T012 [P] Implement environment-backed settings and defaults from `contracts/configuration.md` in `src/config.py`.
- [X] T013 Implement SQLite schema initialization, foreign-key enforcement, migration versioning, and ordered `journey_locations`/`result_locations` relations in `src/persistence/sqlite_adapter.py`.
- [X] T014 [P] Add reusable deterministic routing fixtures, symmetric/asymmetric matrices, and route geometry fixtures in `tests/fixtures/routing_fixtures.py`.
- [X] T015 [P] Add foundational model, cost, and error tests in `tests/unit/test_domain_models.py`, `tests/unit/test_costs.py`, and `tests/unit/test_errors.py`.
- [X] T016 Add persistence adapter integration tests for transactions, foreign keys, ordering, and location deletion rules in `tests/integration/test_sqlite_adapter.py`.
- [X] T017 Add application package initializers and dependency boundaries in `src/domain/__init__.py`, `src/application/__init__.py`, `src/routing/__init__.py`, `src/persistence/__init__.py`, and `src/presentation/__init__.py`.

**Checkpoint**: Domain models, ports, configuration, SQLite persistence, and deterministic fixtures are ready for story work.

---

## Phase 3: User Story 1 - Optimize a Multi-Point Journey (Priority: P1) MVP

**Goal**: Let a traveler manage the points for one journey and obtain an exact lowest-cost route
with fixed endpoint rules and every required intermediate point visited once.

**Independent Test**: Use deterministic route fixtures with a fixed origin, destination, and three
intermediate points whose optimal order differs from the input order. Confirm the returned route is
valid, exact, and lower-cost than every other permitted ordering.

### Tests for User Story 1

- [X] T018 [P] [US1] Add exact optimizer tests for zero, one, two, and multiple points in `tests/unit/test_optimizer.py`.
- [X] T019 [P] [US1] Add optimizer tests for duplicate points, fixed origin/destination, and non-input optimal order in `tests/unit/test_optimizer.py`.
- [X] T020 [P] [US1] Add optimizer tests for symmetric and asymmetric route costs, unreachable segments, and route-information reuse in `tests/unit/test_optimizer.py`.
- [X] T021 [P] [US1] Add use-case acceptance tests for valid optimization and exact result metadata in `tests/e2e/test_optimize_journey.py`.

### Implementation for User Story 1

- [X] T022 [US1] Implement bounded exhaustive permutation optimization with fixed endpoints, route validity, factorial-limit enforcement, and evaluation metrics in `src/domain/optimizer.py`.
- [X] T023 [US1] Implement the optimize-journey application service with validation, directional route caching, categorized failures, and exactness metadata in `src/application/optimize_journey.py`.
- [X] T024 [P] [US1] Implement a deterministic routing adapter for local development and tests in `src/routing/adapters/deterministic.py`.
- [X] T025 [US1] Implement the journey point list, add, modify, delete, endpoint selection, and optimize controls in `src/presentation/journey_window.py`.
- [X] T026 [US1] Implement Tkinter worker-thread dispatch and completion/error callbacks so optimization does not block the GUI event loop in `src/presentation/journey_window.py`.
- [X] T027 [US1] Wire the desktop entry point and dependency composition in `src/app.py`.
- [X] T028 [US1] Add the end-to-end journey setup and optimization flow in `tests/e2e/test_optimize_journey.py`.

**Checkpoint**: A traveler can enter journey points, optimize a bounded journey, and inspect an exact ordered route independently of later cost-selection and map enhancements.

---

## Phase 4: User Story 2 - Choose the Journey Cost (Priority: P2)

**Goal**: Allow travelers to select distance, duration, monetary cost, or explicit weighted criteria
and understand which criterion and weights produced the route.

**Independent Test**: Run the same journey against two criteria with deterministic metrics that yield
different route orders, then verify each result's criterion, weights, and total cost.

### Tests for User Story 2

- [X] T029 [P] [US2] Add acceptance tests for distance, duration, and monetary criteria in `tests/unit/test_cost_criteria.py`.
- [X] T030 [P] [US2] Add weighted-cost tests for valid weights, zero/negative weights, missing metrics, and reported weight snapshots in `tests/unit/test_cost_criteria.py`.
- [X] T031 [P] [US2] Add criteria-selection and invalid-configuration tests for the application service in `tests/e2e/test_cost_selection.py`.

### Implementation for User Story 2

- [X] T032 [US2] Extend the cost criterion controls and weighted metric inputs with validation messages in `src/presentation/journey_window.py`.
- [X] T033 [US2] Integrate selected criteria and explicit weight maps into Journey creation and optimization requests in `src/application/optimize_journey.py`.
- [X] T034 [US2] Ensure optimization results persist and expose criterion, weight snapshots, per-metric totals, and total cost in `src/domain/models.py` and `src/persistence/sqlite_adapter.py`.
- [X] T035 [US2] Add cost criterion and weight display to the result summary in `src/presentation/journey_window.py`.
- [X] T036 [US2] Add end-to-end coverage proving different criteria can produce different valid route orders in `tests/e2e/test_cost_selection.py`.

**Checkpoint**: Travelers can choose and verify the objective used for route optimization without changing the route domain or provider contracts.

---

## Phase 5: User Story 3 - Understand and Recover from Route Results (Priority: P3)

**Goal**: Display saved route results on a map, preserve journey and result records, and provide
clear categorized recovery paths for invalid, unreachable, unavailable, and timed-out journeys.

**Independent Test**: Save a successful journey and result, reopen it, display available geometry,
and submit invalid, unreachable, provider-failure, timeout, and over-limit cases to verify actionable
messages and no misleading fallback route.

### Tests for User Story 3

- [X] T037 [P] [US3] Add persistence tests for saving/loading journeys, results, ordered points, metrics, and geometry in `tests/integration/test_saved_results.py`.
- [X] T038 [P] [US3] Add categorized error acceptance tests for invalid coordinates, unreachable points, provider failure, timeout, unsupported configuration, and resource limit in `tests/e2e/test_failure_handling.py`.
- [X] T039 [P] [US3] Add map-view tests for markers, route geometry, and unavailable-geometry state in `tests/e2e/test_map_view.py`.

### Implementation for User Story 3

- [X] T040 [US3] Implement saved journey and optimization-result load/save workflows in `src/application/journey_persistence.py`.
- [X] T041 [US3] Implement the `tkintermapview` map adapter with point markers, route geometry rendering, fit-to-route behavior, and unavailable-geometry state in `src/presentation/map_view.py`.
- [X] T042 [US3] Integrate map updates, saved-result loading, and persistence actions into `src/presentation/journey_window.py`.
- [X] T043 [US3] Add provider-adapter timeout translation, unavailable-segment handling, and failure recovery in `src/routing/adapters/` and `src/application/optimize_journey.py`.
- [X] T044 [US3] Add user-readable categorized error presentation and retry/reset behavior in `src/presentation/journey_window.py`.
- [X] T045 [US3] Add end-to-end persistence, map display, and failure recovery coverage in `tests/e2e/test_failure_handling.py` and `tests/e2e/test_map_view.py`.

**Checkpoint**: Successful routes are explainable, persisted, and visible on the map; failures are explicit and recoverable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete workflow, operational setup, and constitution-aligned quality gates.

- [X] T046 [P] Add provider-adapter integration tests with deterministic fixtures and timeout behavior in `tests/integration/test_routing_adapters.py`.
- [X] T047 [P] Add application metrics assertions for point count, algorithm, evaluation count, provider requests, and elapsed time in `tests/unit/test_optimization_metrics.py`.
- [X] T048 [P] Document Docker SQLite volume lifecycle, configuration, provider credentials, and troubleshooting in `README.md`.
- [X] T049 Review source modules for dependency direction, secret handling, categorized errors, and exact/approximate result labeling against the constitution in `src/` and `README.md`.
- [X] T050 Run the complete automated suite and the scenarios in `specs/001-multi-point-ride-optimizer/quickstart.md`.
- [X] T051 [P] Add packaging and desktop launch instructions for the supported Python/Tkinter environments in `README.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; tasks T001-T006 can be started immediately.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 and delivers the MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 2; integrates with the US1 optimizer and can be developed after the shared domain exists.
- **User Story 3 (Phase 5)**: Depends on Phase 2; integrates with the US1 result and US2 criterion metadata for the complete saved/map workflow.
- **Polish (Phase 6)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2 or US3.
- **US2 (P2)**: Starts after Phase 2; uses the shared optimizer and cost model, with focused tests independent of the GUI.
- **US3 (P3)**: Starts after Phase 2; requires result and criterion shapes from US1/US2 for complete persistence and presentation, but its adapter and failure tests can begin independently.

### Within Each User Story

- Tests are written before their implementation tasks and must fail before implementation begins.
- Domain models and ports precede application services.
- Application services precede GUI integration.
- Core behavior is validated before persistence/map integration.
- Each checkpoint must pass before the next story is treated as complete.

### Parallel Opportunities

- Phase 1: T003-T006 can run in parallel after T001/T002 establish the project metadata.
- Phase 2: T007-T012 and T014-T015 can run in parallel; T013 depends on the persistence port and models.
- US1: T018-T21 can run in parallel; T024 and T025 can run in parallel after shared ports exist.
- US2: T029-T031 can run in parallel; T032 and T035 are separate GUI work once T033 defines the use-case shape.
- US3: T037-T039 can run in parallel; T041 and T043 can run in parallel after the result model exists.
- Polish: T046-T048 and T051 can run in parallel.
- Different story teams can work concurrently after Phase 2, subject to shared-file coordination in `journey_window.py`.

## Parallel Example: User Story 1

```text
Task T018: Add boundary optimizer tests in tests/unit/test_optimizer.py
Task T019: Add endpoint and ordering optimizer tests in tests/unit/test_optimizer.py
Task T020: Add asymmetric/reuse optimizer tests in tests/unit/test_optimizer.py
Task T021: Add use-case acceptance tests in tests/e2e/test_optimize_journey.py
Task T024: Implement deterministic routing adapter in src/routing/adapters/deterministic.py
Task T025: Implement point management controls in src/presentation/journey_window.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational models, ports, configuration, SQLite adapter, and fixtures.
3. Complete Phase 3 US1 exact optimizer, deterministic adapter, point management, and GUI workflow.
4. Run the independent US1 test suite and the first two quickstart scenarios.
5. Demonstrate the bounded exact route before adding additional cost criteria or saved map workflows.

### Incremental Delivery

1. Deliver US1 as the first usable route-optimization desktop slice.
2. Add US2 to support all configured cost criteria and explainable weighted results.
3. Add US3 to persist results, display route geometry, and recover from categorized failures.
4. Complete cross-cutting verification and package the desktop workflow.

## Notes

- Every task starts with `- [ ]`, has a sequential `T###` ID, and includes `[P]` only when parallelizable.
- User-story tasks include exactly one story label: `[US1]`, `[US2]`, or `[US3]`.
- Paths are explicit and follow the project structure in `plan.md`.
- `tasks.md` does not include implementation code; it is ready for `/speckit-implement`.
