# Persistence Port Contract

The persistence boundary stores and retrieves normalized domain records without exposing SQLite
connections, SQL statements, or Docker details to the domain and application services.

## Operations

- Create, update, list, and delete Locations.
- Create and retrieve Journeys with their ordered point references and cost criterion.
- Save and retrieve Optimization Results with route metrics, exactness, and metadata.
- Delete a Location and transactionally remove saved Journeys and Results that reference it.

## Behavioral Rules

- Writes are transactional and either complete or leave no partial aggregate.
- Foreign-key relationships are enforced.
- Stored ordered point references preserve journey order.
- Timestamps are recorded for mutable records and results.
- Database initialization and migrations are repeatable.
- Configuration supplies the database path; credentials and secrets are not embedded in source.
- Deleting a referenced Location removes its dependent saved route history in the same transaction,
  so the UI cannot leave a point present while silently failing to persist the deletion.
