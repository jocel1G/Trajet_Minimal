# Configuration Contract

Configuration is supplied through environment variables or an equivalent secure configuration
source. Defaults are suitable for local development and do not contain secrets.

| Setting | Required | Default | Meaning |
|---------|----------|---------|---------|
| `RIDE_OPTIMIZER_DB_PATH` | No | `data/ride_optimizer.sqlite3` | Host path to the Docker-mounted SQLite file. |
| `RIDE_OPTIMIZER_EXACT_POINT_LIMIT` | No | `10` | Maximum points for exact optimization. |
| `RIDE_OPTIMIZER_PROVIDER_TIMEOUT_SECONDS` | No | `10` | Maximum wait for one route-source request. |
| `RIDE_OPTIMIZER_ROUTING_PROVIDER` | No | deterministic fixture in tests | Selected routing adapter. |
| Provider credential variables | Provider-dependent | None | Secret values supplied only through secure configuration. |

Invalid numeric settings, missing required provider settings, and unsupported provider names must
produce a startup or request configuration error with no secret values in the message.