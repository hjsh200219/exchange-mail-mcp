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


## TDD 필수

모든 새 기능/로직 변경은 반드시 TDD로 개발한다.
1. Red: 실패하는 테스트 먼저 작성
2. Green: 테스트를 통과하는 최소 코드 작성
3. Refactor: 코드 정리
테스트 없는 코드 변경은 허용하지 않는다.
