import logging
import sys

# MCP communicates over stdio. Redirect all logging to stderr so nothing
# from this process or its dependencies can corrupt the JSON-RPC stream on stdout.
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

from mcp.server.fastmcp import FastMCP

from workshop_extension.mcp.hello import register_hello
from workshop_extension.weather.mcp import register_weather_check
from workshop_extension.transit.mcp import register_transit_arrivals, register_transit_stops
from workshop_extension.gui.mcp import register_gui_server

app = FastMCP(name="workshop-extension")

_ = register_hello(app)
_ = register_weather_check(app)
_ = register_transit_arrivals(app)
_ = register_transit_stops(app)
_ = register_gui_server(app)


def main():
    """Entry point for the MCP server."""
    try:
        app.run()
    except (BrokenPipeError, EOFError):
        # stdio transport closed by the client (normal shutdown).
        sys.exit(0)
    except Exception as e:
        print(
            f"workshop-extension MCP server error: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
