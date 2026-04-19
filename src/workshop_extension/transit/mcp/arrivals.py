from mcp.server.fastmcp import FastMCP


def register_transit_arrivals(app: FastMCP) -> FastMCP:
    from typing import Union

    from workshop_extension.mcp.types import ToolSuccess, ToolError
    from workshop_extension.mcp.utils import tool_success, tool_error
    from workshop_extension.transit.client import get_arrivals

    @app.tool(
        title="PRT Bus Arrivals",
        description=(
            "Get upcoming Pittsburgh Regional Transit (PRT) bus arrival times at a stop. "
            "Requires PRT_API_KEY environment variable (free key from https://truetime.rideprt.org/)."
        ),
        structured_output=True,
    )
    async def transit_arrivals(
        stop_id: str,
        route: str | None = None,
        max_results: int = 5,
    ) -> Union[ToolSuccess[dict], ToolError]:
        """
        Get next bus arrivals at a PRT stop.

        Args:
            stop_id: PRT stop ID number (e.g. "8155" for 5th Ave & Craig St, Oakland).
                     Find stop IDs at https://truetime.rideprt.org/ or via transit_stops.
            route: Optional route to filter by (e.g. "61C", "71A"). Shows all routes if omitted.
            max_results: How many upcoming arrivals to return (default 5).
        """
        try:
            arrivals = get_arrivals(stop_id=stop_id, route=route, max_results=max_results)
            return tool_success({"stop_id": stop_id, "arrivals": arrivals})
        except RuntimeError as e:
            return tool_error(str(e), "PRT_API_ERROR")
        except Exception as e:
            return tool_error(
                f"Failed to fetch arrivals for stop {stop_id}",
                "ARRIVALS_FETCH_FAILED",
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = transit_arrivals
    return app
