from mcp.server.fastmcp import FastMCP


def register_hello(app: FastMCP) -> FastMCP:
    @app.tool()
    def hello_world(name: str = "World") -> str:
        """Say hello. Replace this with your first real tool."""
        return f"Hello, {name}!"

    return app
