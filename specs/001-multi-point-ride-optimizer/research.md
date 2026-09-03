# Research: Multi-Point Ride Optimizer

## Decision 1: Use Python 3.11+ with Tkinter for the desktop shell

- **Decision**: Use Python 3.11 or newer and the standard Tkinter toolkit for the desktop GUI.
- **Rationale**: Tkinter is available with standard Python distributions, is sufficient for a
  focused single-user desktop workflow, and keeps presentation concerns separate from the domain.
  Python 3.11 provides current typing, testing, and performance improvements while maintaining a
  broad desktop support range.
- **Alternatives considered**: Qt bindings would provide a richer widget set but add a larger
  dependency and licensing/distribution decision. A web desktop shell would introduce a browser
  runtime and violate the deliberately small desktop scope.

## Decision 2: Use a provider-neutral routing port and a map adapter

- **Decision**: Define an internal routing capability that returns normalized route segments and
  optional route geometry. Implement the first map display with `tkintermapview`, while keeping its
  types out of the domain and application layers.
- **Rationale**: The constitution requires provider-agnostic routing. A normalized port allows a
  deterministic fixture provider for tests and lets the map widget or external routing source be
  replaced independently.
- **Alternatives considered**: Calling a mapping SDK directly from the optimizer was rejected because
  it couples business logic to a provider. A static image map was rejected because the user needs a
  route displayed on a navigable map.

## Decision 3: Use an exact permutation optimizer for the initial bounded scope

- **Decision**: Use exhaustive permutations for journeys up to 10 points, with fixed origin and
  optional fixed destination and every required intermediate point visited once. Reject requests
  above the configured exact limit until an approximation strategy is explicitly added.
- **Rationale**: Exhaustive evaluation is easy to verify against deterministic fixtures and directly
  satisfies correctness-first requirements for the initial scope. The explicit limit prevents an
  unrestricted factorial algorithm.
- **Alternatives considered**: Nearest-neighbor and 2-opt are faster for larger journeys but are
  approximate and would require additional result semantics and quality validation. Dynamic
  programming may be added later behind the same optimizer port.

## Decision 4: Represent cost as a validated domain value object

- **Decision**: Support distance, duration, monetary cost, and weighted combinations. Weighted
  criteria require non-negative explicit weights and at least one positive weight; all requested
  metrics must be available for the route being compared.
- **Rationale**: Explicit validation prevents ambiguous optimization and makes results explainable.
  Cost computation remains independent of UI, routing providers, and persistence.
- **Alternatives considered**: Embedding criterion selection in the GUI was rejected because it
  prevents reuse and makes the optimizer difficult to test.

## Decision 5: Persist through a SQLite adapter with Docker-managed data

- **Decision**: Use SQLite as the durable store, accessed through a persistence port and the Python
  standard-library `sqlite3` adapter. Docker Compose owns the database file's mounted `data/`
  volume and runs schema initialization/maintenance; the desktop process uses the same configured
  file path through the adapter.
- **Rationale**: SQLite is appropriate for a single-user desktop workload and requires no database
  server protocol. A mounted Docker volume satisfies the requested Docker placement while keeping
  the domain unaware of Docker. The adapter can enforce transactions, foreign keys, and migrations.
- **Alternatives considered**: PostgreSQL in Docker would offer a network database service but adds
  operational overhead beyond the single-user scope. Storing directly in an untracked local file
  would not satisfy the Docker requirement.

## Decision 6: Keep optimization synchronous in the use case but off the Tkinter event loop

- **Decision**: The application use case remains deterministic and directly testable; the GUI invokes
  it through a worker boundary and posts completion or categorized failure back to the Tkinter UI.
- **Rationale**: This keeps the domain simple while preventing provider latency or exhaustive search
  from freezing the desktop window.
- **Alternatives considered**: Running all work directly in button callbacks was rejected because it
  makes the GUI unresponsive during route calculation.

## Decision 7: Treat map geometry as optional result data

- **Decision**: A successful optimization always returns ordered points and metrics. It includes route
  geometry when the routing source supplies it; the GUI displays a clear unavailable-geometry state
  otherwise.
- **Rationale**: Optimization can be tested with distance matrices and deterministic fixtures that do
  not provide map polylines, while real providers can render the route on the map.
- **Alternatives considered**: Making geometry mandatory would unnecessarily prevent offline and unit
  test providers from producing valid optimization results.
