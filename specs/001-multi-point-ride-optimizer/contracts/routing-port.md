# Routing Port Contract

The application consumes route information through a provider-neutral boundary. A routing adapter
MUST translate provider responses into the normalized Route Segment model before returning them.

## Request

- `origin`: a validated Location
- `destination`: a validated Location
- `criteria`: requested metrics needed to calculate route cost
- `timeout`: maximum permitted provider wait

## Response

A normalized route segment containing:

- Directional origin and destination identifiers
- Reachability
- Available distance, duration, and monetary cost
- Optional route geometry
- Provider metadata

The response MUST distinguish an unreachable segment from a provider failure and from missing metric
data. Provider-specific response fields MUST NOT leak through this boundary.

## Behavioral Rules

- Invalid coordinates are rejected before the adapter request.
- Provider calls have a timeout.
- Repeated requests for the same directional pair and metric set are reused within one optimization.
- A provider failure never becomes a fabricated route segment.
- Directional pairs are cached separately to preserve asymmetric costs.
