from mcp.server.fastmcp import FastMCP


def register_gui_server(app: FastMCP) -> FastMCP:
    from typing import Union

    from workshop_extension.mcp.types import ToolSuccess, ToolError
    from workshop_extension.mcp.utils import tool_success, tool_error
    from workshop_extension.gui.lifecycle import (
        DEFAULT_HOST,
        DEFAULT_PORT,
        _is_port_in_use,
        start_gui_server,
        stop_gui_server,
    )

    @app.tool(
        title="GUI Server",
        description=(
            "Manage the workshop-extension weather GUI. "
            "Use action='start' to launch the GUI and open it in the browser. "
            "Use action='stop' to shut it down."
        ),
        structured_output=True,
    )
    async def gui_server(
        action: str,
        host: str | None = None,
        port: int | None = None,
    ) -> Union[ToolSuccess[dict], ToolError]:
        """
        Manage the Pittsburgh weather GUI server.

        Args:
            action: "start" or "stop".
            host: Bind address (default 127.0.0.1).
            port: Port (default 24880).
        """
        bind_host = host or DEFAULT_HOST
        bind_port = port or DEFAULT_PORT

        if action == "start":
            outcome = start_gui_server(host=bind_host, port=bind_port)
            if outcome.get("error"):
                return tool_error(outcome["error"], "SERVER_LAUNCH_FAILED")
            return tool_success({
                "pid": outcome["pid"],
                "server_url": outcome["server_url"],
                "reused": outcome["reused"],
                "message": (
                    f"GUI {'already running' if outcome['reused'] else 'started'} "
                    f"at {outcome['server_url']}."
                ),
            })

        if action == "stop":
            killed = stop_gui_server()
            if not killed:
                return tool_error("No running GUI server found.", "PROCESS_NOT_FOUND")
            return tool_success({
                "killed_pids": killed,
                "message": f"Stopped {len(killed)} process(es): {', '.join(str(p) for p in killed)}.",
            })

        return tool_error(
            f"Unknown action: {action!r}. Use 'start' or 'stop'.",
            "INVALID_ACTION",
            action=action,
        )

    _ = gui_server
    return app
