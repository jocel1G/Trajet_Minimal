# Implementation Plan: Multi-Point Ride Optimizer

**Branch**: `001-multi-point-ride-optimizer` | **Date**: 2026-09-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-multi-point-ride-optimizer/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Provide a desktop workflow for creating, editing, deleting, and optimizing journey points. The
application will calculate an exact route for small journeys using a provider-independent routing
port and an explicit cost model, display the result on a map, and persist journey points and
optimization results in SQLite hosted in a Docker container with a mounted data volume.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Tkinter, tkintermapview, pytest, Docker Compose; stdlib `sqlite3` and
`itertools` for persistence and the initial exact optimizer

**Storage**: SQLite database in a Docker container, persisted through a mounted host volume;
application access uses a persistence adapter

**Testing**: pytest unit tests for domain and optimizer, adapter integration tests with deterministic
fixtures, and GUI-independent end-to-end use-case tests

**Target Platform**: Desktop environments supported by Python 3.11 and Tkinter; Docker Desktop for
the SQLite container

**Project Type**: Desktop application

**Performance Goals**: Exact optimization for journeys up to 10 points completes within 5 seconds,
excluding routing-provider latency; GUI remains responsive by running route calculation outside the
event-handling path

**Constraints**: Exact optimization has an explicit point limit; unsupported metrics, invalid
coordinates, unreachable points, provider failures, and timeouts produce categorized errors; map
display requires available route geometry or a clear unavailable-map state

**Scale/Scope**: Single-user desktop workflow, one active journey at a time, up to 10 points for
the initial exact strategy; persistence supports saved journey points and saved optimal routes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Optimal Route Is the Primary Domain Invariant**: PASS. The optimizer is a domain service
  with explicit valid-route and cost rules, isolated from GUI, storage, and providers.
- **II. Provider-Agnostic Routing**: PASS. Route acquisition is defined by an internal port and
  provider adapters; the design does not expose provider-specific models to the optimizer.
- **III. Correctness Before Optimization**: PASS. Deterministic tests cover the specified boundary,
  duplicate, invalid, unreachable, symmetric, asymmetric, and fixed-endpoint cases.
- **IV. Algorithm Selection Must Match Problem Size**: PASS. The initial exact permutation strategy
  is limited to 10 points and its factorial complexity is documented; replacement remains possible.
- **V. Cost Calculation Must Be Explicit**: PASS. Distance, duration, monetary cost, and weighted
  criteria are separate domain concepts with explicit weights.
- **VI. Separation of Concerns**: PASS. Presentation, use case, domain, routing, and persistence
  adapters have separate modules and dependency directions.
- **VII. Observable and Explainable Results**: PASS. Results persist and expose ordered points,
  metrics, criterion, exactness, and algorithm/provider metadata.
- **VIII. Performance Must Be Measurable**: PASS. The design records evaluation and provider-request
  counts and elapsed optimization time, with route-information reuse within a request.
- **IX. Failure Must Be Explicit**: PASS. Categorized domain errors and exact/approximate status are
  part of the use-case result; no fallback is labeled optimal.
- **Technical Constraints, Performance, Security**: PASS. Strong domain models, adapters, Docker
  volume persistence, input validation, secrets via environment configuration, and provider timeouts
  are included in the design.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
```text
src/
├── app.py
├── domain/
│   ├── models.py
│   ├── costs.py
│   ├── errors.py
│   └── optimizer.py
├── application/
│   └── optimize_journey.py
├── routing/
│   ├── port.py
│   └── adapters/
├── persistence/
│   ├── port.py
│   └── sqlite_adapter.py
└── presentation/
    ├── journey_window.py
    └── map_view.py

tests/
├── unit/
├── integration/
└── e2e/

docker/
└── docker-compose.yml

data/
└── .gitkeep

requirements.txt
pyproject.toml
README.md
```

**Structure Decision**: Use a single Python desktop project with domain-first modules under `src/`.
The Tkinter presentation layer depends on application use cases, while domain modules depend only
on domain types and ports. Routing and SQLite adapters implement those ports. Docker configuration
is isolated under `docker/`, and the host-mounted `data/` directory stores the database file without
putting Docker concerns into the domain.

## Complexity Tracking

No constitution violations. The Dockerized SQLite process is an operational boundary required by
the user request and is kept behind the persistence adapter; it does not add a domain dependency.
