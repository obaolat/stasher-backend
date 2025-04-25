
# Stasher Backend Interview Challenge – Enhanced Stashpoint Search

This project builds on the base Stasher backend by adding a powerful search endpoint that filters stashpoints by location, time, capacity, and business hours. All logic and routes live under **`/api/v1/stashpoints/`**, with strict parameter validation and clear error handling.

## Setup

1. Clone the repo and enter the directory:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```
2. Start services:
   ```bash
   docker-compose up -d
   ```
3. Verify:
   ```bash
   curl http://localhost:5000/healthcheck
   ```

## Endpoints

**1. List all stashpoints (no filters)**  
```
GET /api/v1/stashpoints/
```
Returns every stashpoint in the database, unfiltered.

**2. Search available stashpoints**  
Requires **exactly** these query parameters (any missing, extra or malformed ⇒ HTTP 400/404):

- `lat` (float)  
- `lng` (float)  
- `dropoff` (ISO 8601 datetime)  
- `pickup` (ISO 8601 datetime, must be after `dropoff`)  
- `bag_count` (integer > 0)  
- `radius_km` (float)

```
GET /api/v1/stashpoints/?lat=51.5074&lng=-0.1278&dropoff=2023-04-20T10:00:00&pickup=2023-04-20T18:00:00&bag_count=2&radius_km=1
```

> **Note:** In Python versions prior to 3.11, `datetime.fromisoformat()` does not support parsing the `'Z'` suffix (which represents UTC time). Therefore, **you must remove the `'Z'`** or convert it to `+00:00` before parsing. Otherwise, your request will return a `400` error.

```python
from datetime import datetime

# This will raise an error in Python < 3.11
# dropoff = datetime.fromisoformat("2023-04-20T10:00:00Z")

# Correct way for compatibility
dropoff = datetime.fromisoformat("2023-04-20T10:00:00".replace("Z", "+00:00"))
pickup = datetime.fromisoformat("2023-04-20T18:00:00".replace("Z", "+00:00"))
```

**Response** (HTTP 200 – filtered & sorted by distance):
```json
[
  {
    "id": "55b4c04fcdde40ff801dd36cd013ff34",
    "name": "Central Cafe Storage",
    "address": "123 Main Street",
    "postal_code": "EC1A 1AA",
    "latitude": 51.5107,
    "longitude": -0.1246,
    "distance_km": 0.43,
    "capacity": 20,
    "available_capacity": 20,
    "open_from": "08:00",
    "open_until": "22:00",
    "description": "Cafe in the heart of the city with secure bag storage"
  }
]
```

## Behavior & Validation

- **All parameters required** for search.  
- **Extra or unknown parameters** ⇒ HTTP 404.  
- **Missing or malformed parameters** ⇒ HTTP 400.  
- `dropoff` ≥ `pickup` ⇒ HTTP 400 (“Dropoff time must be before pickup time”).  
- `bag_count` ≤ 0 ⇒ HTTP 400 (“Bag count must be greater than 0”).  

## Implementation Highlights

- **Geography datatype** & PostGIS functions for accurate distance & radius filtering.  
- **Subquery** to sum overlapping bookings and compute live available capacity.  
- **Indexed** spatial column (`location`) for performance.  
- **Clear, modular code** for maintainability and easy extension.  

## Future Improvements

- Add unit/integration tests covering edge cases.  
- Time-zone support for global use.  
- Pagination for large result sets.  
- Caching or materialized views for high-traffic scenarios.

---
*This README is tailored for an interview submission: concise, complete, and ready to copy-paste.*
