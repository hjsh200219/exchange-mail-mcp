# Exchange Mail MCP

Microsoft 365 Exchange mail MCP server using Graph API with Device Code Flow authentication.

## Structure

- `config.py` - Shared constants (CLIENT_ID, AUTHORITY, SCOPES, TOKEN_CACHE_FILE)
- `server.py` - MCP server (FastMCP). Tools: check_exchange_mail, read_exchange_mail, search_exchange_mail
- `auth.py` - Standalone auth script for device code login/refresh
- `pyproject.toml` - Project config. Entry points: `exchange-mail-mcp`, `exchange-mail-auth`

## Auth

- Device Code Flow via MSAL
- Token cache: `~/.ms_token_cache.json` (override with `MS_TOKEN_CACHE` env)
- Client ID: `MS_CLIENT_ID` env or hardcoded default
- Scope: `Mail.Read`

## Dev

```bash
uv run exchange-mail-auth   # Initial login
uv run exchange-mail-mcp    # Start MCP server (stdio)
```

> Be concise. No filler. Straight to the point. Use fewer words.
