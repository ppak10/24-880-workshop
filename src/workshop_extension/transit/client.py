"""Pittsburgh Regional Transit (PRT) TrAMS real-time API client.

Requires a free API key from https://truetime.rideprt.org/
Set the environment variable PRT_API_KEY before starting the MCP server.
"""

import os
import httpx

BASE_URL = "https://truetime.rideprt.org/bustime/api/v3"


def _key() -> str:
    key = os.environ.get("PRT_API_KEY", "")
    if not key:
        raise RuntimeError(
            "PRT_API_KEY environment variable is not set. "
            "Register for a free key at https://truetime.rideprt.org/"
        )
    return key


def get_arrivals(stop_id: str, route: str | None = None, max_results: int = 5) -> list[dict]:
    """
    Return upcoming bus arrivals at a PRT stop.

    Args:
        stop_id: PRT stop ID (e.g. "8155" for 5th Ave & Craig St in Oakland).
        route: Optional route filter (e.g. "61C"). If omitted, all routes are returned.
        max_results: Maximum number of predictions to return.

    Returns:
        List of dicts with keys: route, destination, arrival_time, minutes, delayed.
    """
    params: dict = {
        "key": _key(),
        "stpid": stop_id,
        "format": "json",
        "tmres": "m",
    }
    if route:
        params["rt"] = route

    resp = httpx.get(f"{BASE_URL}/getpredictions", params=params, timeout=10)
    resp.raise_for_status()
    body = resp.json().get("bustime-response", {})

    error = body.get("error")
    if error:
        msg = error[0].get("msg", "Unknown error") if isinstance(error, list) else str(error)
        raise RuntimeError(f"PRT API error: {msg}")

    predictions = body.get("prd", [])[:max_results]
    results = []
    for p in predictions:
        results.append({
            "route": p.get("rt", ""),
            "destination": p.get("des", ""),
            "arrival_time": p.get("prdtm", ""),
            "minutes": p.get("prdctdn", ""),
            "delayed": p.get("dly", False),
        })
    return results


def get_stops(route: str, direction: str) -> list[dict]:
    """
    Return stops for a PRT route/direction.

    Args:
        route: Route number (e.g. "61C").
        direction: Direction label as returned by PRT (e.g. "INBOUND", "OUTBOUND").

    Returns:
        List of dicts with keys: stop_id, stop_name, lat, lon.
    """
    params = {
        "key": _key(),
        "rt": route,
        "dir": direction,
        "format": "json",
    }
    resp = httpx.get(f"{BASE_URL}/getstops", params=params, timeout=10)
    resp.raise_for_status()
    body = resp.json().get("bustime-response", {})

    error = body.get("error")
    if error:
        msg = error[0].get("msg", "Unknown error") if isinstance(error, list) else str(error)
        raise RuntimeError(f"PRT API error: {msg}")

    return [
        {
            "stop_id": s.get("stpid", ""),
            "stop_name": s.get("stpnm", ""),
            "lat": s.get("lat"),
            "lon": s.get("lon"),
        }
        for s in body.get("stops", [])
    ]
