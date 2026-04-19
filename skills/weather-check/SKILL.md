---
name: weather-check
description: Check current weather and umbrella recommendation for a Pittsburgh-area location.
---

# Weather Check

Check Pittsburgh weather and get a direct umbrella recommendation.

## When to Use

- User asks if they need an umbrella
- User asks about rain, precipitation, or weather conditions
- User asks what to wear or whether to bring a jacket
- User mentions a specific Pittsburgh destination and wants to know conditions there

## Steps

1. Identify the location from the user's message. Default to **Pittsburgh, PA** if none is given.
   - Recognize neighborhoods: "CMU" → Carnegie Mellon / Oakland, "downtown" → Downtown Pittsburgh, "the Strip" → Strip District, etc.
2. Call `weather_check(location=<location>)`.
3. Respond with:
   - **Umbrella verdict first** — a clear yes or no.
   - Current temperature and conditions.
   - Today's precipitation probability and expected amount.
   - One sentence of context if helpful (e.g. "Rain is expected to start in the afternoon.").

## Example Response Format

> **Yes, bring an umbrella.** It's currently 54°F with light rain in Oakland. There's a 78% chance of rain today with 0.4" expected. Conditions should persist through the evening.

> **No umbrella needed.** It's 68°F and partly cloudy in Downtown Pittsburgh. Rain probability is only 12% today.

## Notes

- `weather_check` uses Open-Meteo — no API key required, always available.
- If the geocoder can't find the location, it defaults to central Pittsburgh.
- For transit timing alongside weather, use the commute-check skill instead.
