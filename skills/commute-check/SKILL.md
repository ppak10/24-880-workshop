---
name: commute-check
description: Combined Pittsburgh commute check — weather conditions plus PRT bus arrival times for a route and stop.
---

# Commute Check

Run a full commute check: weather at the destination and next bus arrivals at a stop.

## When to Use

- User asks about their commute, trip, or travel plans
- User wants weather AND transit info together
- User asks "when is the next bus" alongside weather questions

## Prerequisites

Transit tools require `PRT_API_KEY` to be set. If it is not set, complete the weather portion and inform the user:

> Transit arrivals are unavailable — `PRT_API_KEY` is not set. Register for a free key at https://truetime.rideprt.org/ and add it to your environment.

## Steps

### 1. Check Weather

Call `weather_check(location=<destination>)` and note the umbrella verdict.

### 2. Look Up Bus Arrivals (if PRT_API_KEY is set)

If the user provided a stop ID, call `transit_arrivals(stop_id=<id>, route=<route>)` directly.

If only a route is known:
1. Call `transit_stops(route=<route>, direction=<direction>)` to list stops.
2. Identify the closest stop to the user's location by name.
3. Call `transit_arrivals(stop_id=<id>)`.

### 3. Combine and Respond

Present weather and transit together:

```
Commute to Oakland:
• Umbrella: YES — 72% rain probability, light rain expected
• Temperature: 56°F, Light rain
• Next 61C arrivals at Craig St & 5th Ave (stop 8155):
    - 2 min (route 61C → Squirrel Hill)
    - 14 min (route 61C → Squirrel Hill)
    - 28 min (route 61C → Squirrel Hill)
```

## Common PRT Routes

| Route | Corridor |
|-------|----------|
| 61A/B/C/D | East Busway → Oakland → various East End destinations |
| 71A/B/C/D | East Busway → Oakland / Squirrel Hill / Point Breeze |
| 28X | Airport Flyer → Downtown → Oakland |
| 54C | Northside → Downtown → Oakland |
| P1/P2/P3 | Silver Line (bus rapid transit) — eastern suburbs |

## Notes

- Stop IDs can be found via `transit_stops` or at https://truetime.rideprt.org/
- `max_results` defaults to 5 arrivals; reduce to 3 for a cleaner response.
- Arrival times are in minutes ("DUE" means arriving now).
