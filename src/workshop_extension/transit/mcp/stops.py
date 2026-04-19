from mcp.server.fastmcp import FastMCP


def register_transit_stops(app: FastMCP) -> FastMCP:
    from typing import Union

    from workshop_extension.mcp.types import ToolSuccess, ToolError
    from workshop_extension.mcp.utils import tool_success, tool_error
    from workshop_extension.transit.client import get_stops

    @app.tool(
        title="PRT Route Stops",
        description=(
            "List stops for a Pittsburgh Regional Transit (PRT) route and direction. "
            "Useful for finding stop IDs to use with transit_arrivals. "
            "Requires PRT_API_KEY environment variable."
        ),
        structured_output=True,
    )
    async def transit_stops(
        route: str,
        direction: str = "OUTBOUND",
    ) -> Union[ToolSuccess[dict], ToolError]:
        """
        List stops for a PRT bus route.

        Args:
            route: Route number (e.g. "61C", "71A", "28X").
            direction: "INBOUND" or "OUTBOUND" (default "OUTBOUND").
        """
        try:
            stops = get_stops(route=route, direction=direction.upper())
            return tool_success({"route": route, "direction": direction.upper(), "stops": stops})
        except RuntimeError as e:
            return tool_error(str(e), "PRT_API_ERROR")
        except Exception as e:
            return tool_error(
                f"Failed to fetch stops for route {route}",
                "STOPS_FETCH_FAILED",
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = transit_stops
    return app
