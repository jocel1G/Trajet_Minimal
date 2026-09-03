# Optimization Use-Case Contract

The application use case accepts a validated journey request and returns either an explainable
optimization result or a categorized failure. It does not expose GUI, SQLite, Docker, or provider
SDK types.

## Request

- Ordered locations with one fixed origin and an optional fixed destination.
- Visit policy requiring each intermediate point exactly once.
- Cost criterion: `distance`, `duration`, `monetary_cost`, or `weighted`.
- For `weighted`, a map of non-negative metric weights with at least one positive value.
- Exact point limit and provider timeout from application configuration.

## Success Response

- Ordered location identifiers, with fixed endpoints in their required positions.
- Total distance, duration, and monetary cost when supplied by the routing source.
- Total cost and a snapshot of the selected criterion and weights.
- `exactness` set to `exact` for the initial bounded permutation optimizer.
- Algorithm, provider, evaluated-route count, provider-request count, and elapsed time.
- Optional route geometry for map display.

## Failure Response

The use case returns one stable category: `invalid_input`, `invalid_coordinates`,
`unreachable_location`, `routing_provider_failure`, `optimization_failure`,
`unsupported_configuration`, `timeout`, or `resource_limit`. It does not return a route when the
route cannot be verified under the requested criterion.

## Behavioral Rules

- Validate all locations and criterion weights before any provider request.
- Reuse route information for each directional location pair during one request.
- Reject a request above the exact optimizer's configured point limit.
- Treat missing required metric data as an unavailable-data failure rather than skipping a segment.
- Preserve asymmetric costs by requesting and caching each direction independently.