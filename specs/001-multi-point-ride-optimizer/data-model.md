# Data Model: Multi-Point Ride Optimizer

## Location

Represents a journey point.

| Field | Type | Rules |
|-------|------|-------|
| `id` | identifier | Required and unique within the application. |
| `label` | text | Required, user-readable, and non-empty. |
| `latitude` | decimal | Required; inclusive range -90 to 90. |
| `longitude` | decimal | Required; inclusive range -180 to 180. |
| `created_at` | timestamp | Assigned when first persisted. |
| `updated_at` | timestamp | Updated after modification. |

A location with invalid or missing coordinates MUST be rejected before route lookup.

## Journey

Represents one optimization request and its ordered input points.

| Field | Type | Rules |
|-------|------|-------|
| `id` | identifier | Unique when persisted. |
| `name` | text | Optional user-readable name. |
| `location_ids` | ordered identifiers | Contains the requested points; duplicates are preserved for validation. |
| `origin_id` | identifier | Required for the initial workflow and must be the first result point. |
| `destination_id` | identifier | Optional; when present it must be the last result point. |
| `visit_policy` | enum | Initial value requires each required intermediate point exactly once. |
| `cost_criterion` | Cost Criterion | Required and validated before optimization. |
| `status` | enum | `draft`, `optimizing`, `optimized`, or `failed`. |
| `created_at` | timestamp | Assigned on creation. |
| `updated_at` | timestamp | Updated after changes. |

Rules: the origin and destination must belong to the journey points, and the destination cannot be
identical to the origin. A journey must not be optimized while it has invalid points or an
unsupported criterion.

## Route Segment

Normalized routing data between two locations.

| Field | Type | Rules |
|-------|------|-------|
| `from_location_id` | identifier | Required. |
| `to_location_id` | identifier | Required and direction-sensitive. |
| `status` | enum | `reachable`, `unreachable`, `provider_error`, or `missing_metric`. |
| `distance` | decimal | Non-negative when available. |
| `duration` | decimal | Non-negative when available. |
| `monetary_cost` | decimal | Non-negative when available. |
| `geometry` | coordinate sequence | Optional map path. |

The pair is directional because travel costs may be asymmetric. A segment with any status other than
`reachable` cannot participate in an exact route comparison; the status determines whether the
request is reported as unreachable, a provider failure, or unavailable metric data.

## Cost Criterion

Defines route comparison.

- `distance`: requires distance on every segment.
- `duration`: requires duration on every segment.
- `monetary_cost`: requires monetary cost on every segment.
- `weighted`: contains a JSON object/map of metric names to non-negative numeric weights and requires
  at least one positive weight, for example `{ "distance": 0.6, "duration": 0.4 }`.

For weighted criteria, total cost is the sum of each segment metric multiplied by its explicit
weight. Weights are stored with the Journey and copied into the Optimization Result as a snapshot.
Missing required metrics on any candidate segment fail the optimization with an unavailable-data
error; the system does not skip segments or substitute another metric.

## Optimization Result

Represents a successful or approximate route calculation.

| Field | Type | Rules |
|-------|------|-------|
| `id` | identifier | Unique when persisted. |
| `journey_id` | identifier | References the journey. |
| `ordered_location_ids` | ordered identifiers | Contains each required point according to visit policy. |
| `total_distance` | decimal | Non-negative when available. |
| `total_duration` | decimal | Non-negative when available. |
| `total_monetary_cost` | decimal | Non-negative when available. |
| `total_cost` | decimal | Required and calculated from the selected criterion. |
| `criterion` | Cost Criterion | Snapshot of the criterion used. |
| `exactness` | enum | `exact` or `approximate`; initial implementation produces `exact`. |
| `algorithm` | text | Identifies the optimizer used. |
| `provider` | text | Identifies the route-information source. |
| `evaluated_routes` | integer | Non-negative measurement. |
| `provider_requests` | integer | Non-negative measurement. |
| `elapsed_ms` | decimal | Non-negative measurement. |
| `geometry` | coordinate sequence | Optional combined map path. |
| `created_at` | timestamp | Assigned when persisted. |

## Optimization Error

A categorized failure with a stable category and actionable message. Categories are
`invalid_input`, `invalid_coordinates`, `unreachable_location`, `routing_provider_failure`,
`optimization_failure`, `unsupported_configuration`, `timeout`, and `resource_limit`.

## Relationships and Persistence

- A Journey references one or more Locations through an ordered `journey_locations` relation with
  `journey_id`, `location_id`, and zero-based `position`; the position is unique within a Journey.
- An Optimization Result references its ordered points through an ordered `result_locations`
  relation with `result_id`, `location_id`, and zero-based `position`.
- An Optimization Result belongs to one Journey and references its ordered Locations.
- A Route Segment is transient route lookup data and may be cached for a calculation; it need not be
  persisted independently in the initial release.
- Deleting a Location MUST remove dependent saved Journeys and Optimization Results in the same
  transaction. This keeps the persisted data consistent with the user's explicit deletion.
- SQLite tables SHOULD include foreign keys, transaction boundaries, and migration versioning. The
  ordered relations preserve sequence without relying on a database-specific array type.
