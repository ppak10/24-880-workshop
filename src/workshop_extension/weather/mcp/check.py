from mcp.server.fastmcp import FastMCP


def register_weather_check(app: FastMCP) -> FastMCP:
    from typing import Union

    from workshop_extension.mcp.types import ToolSuccess, ToolError
    from workshop_extension.mcp.utils import tool_success, tool_error
    from workshop_extension.weather.client import umbrella_summary

    @app.tool(
        title="Check Pittsburgh Weather",
        description=(
            "Check the current weather and today's precipitation forecast for a "
            "Pittsburgh-area location. Returns an umbrella recommendation."
        ),
        structured_output=True,
    )
    async def weather_check(
        location: str = "Downtown Pittsburgh",
    ) -> Union[ToolSuccess[dict], ToolError]:
        """
        Check weather and umbrella need for a Pittsburgh-area destination.

        Args:
            location: Neighborhood, landmark, or address in Pittsburgh
                      (e.g. "CMU", "Oakland", "Strip District", "15213").
        """
        try:
            summary = umbrella_summary(location)
            return tool_success(summary)
        except Exception as e:
            return tool_error(
                f"Failed to fetch weather for '{location}'",
                "WEATHER_FETCH_FAILED",
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = weather_check
    return app
