# 24-880-workshop

A boilerplate extension for [Claude Code](https://claude.ai/code) and [Gemini CLI](https://github.com/google-gemini/gemini-cli).

## Structure

```
.
├── gemini-extension.json   # Gemini CLI extension manifest
├── GEMINI.md               # Skill includes injected into Gemini context
├── pyproject.toml          # Python package (uv)
├── src/
│   └── workshop_extension/
│       └── mcp/
│           ├── __init__.py     # FastMCP app + tool registration
│           ├── __main__.py     # Entry point: python -m workshop_extension.mcp
│           └── hello.py        # Example tool (replace with yours)
├── agents/
│   └── workshop.md         # Agent definition (Claude Code subagent)
├── skills/
│   └── hello-world/
│       └── SKILL.md        # Skill definition
└── hooks/
    ├── hooks.json          # SessionStart / SessionEnd hook config
    ├── run-hook.cmd        # Cross-platform hook runner (Windows + Unix)
    ├── session-start       # Runs on session start
    └── session-end         # Runs on session end
```

## Installation

### Claude Code

Add to your `~/.claude/settings.json` (or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "workshop-extension": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/24-880-workshop", "python", "-m", "workshop_extension.mcp"],
      "env": {
        "PYTHONPATH": "/path/to/24-880-workshop/src",
        "WORKSHOP_PROJECT_DIR": "${workspacePath}"
      }
    }
  }
}
```

### Gemini CLI

```bash
gemini extension install /path/to/24-880-workshop
```

The `gemini-extension.json` manifest is picked up automatically.

## Development

```bash
# Install dependencies
uv sync

# Run the MCP server directly (for testing)
uv run python -m workshop_extension.mcp
```

## Adding Tools

1. Create `src/workshop_extension/mcp/my_tool.py` with a `register_my_tool(app)` function
2. Import and register it in `src/workshop_extension/mcp/__init__.py`
3. Add a corresponding skill in `skills/my-skill/SKILL.md`
4. Reference the skill in `GEMINI.md` with `@./skills/my-skill/SKILL.md`
