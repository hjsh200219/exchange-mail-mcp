#!/usr/bin/env python3
"""Standalone auth script for Exchange Mail MCP - run this to login/refresh token."""

import msal
import os
import sys

from config import CLIENT_ID, AUTHORITY, SCOPES, TOKEN_CACHE_FILE


def main():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE) as f:
            cache.deserialize(f.read())

    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print(f"Already authenticated as {accounts[0].get('username', 'unknown')}")
            return

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print(f"Error: {flow}", file=sys.stderr)
        sys.exit(1)

    print(f"\nLogin required:")
    print(f"  1. Open https://login.microsoft.com/device")
    print(f"  2. Enter code: {flow['user_code']}\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())
        print("Authentication successful!")
    else:
        print(f"Failed: {result.get('error_description', result)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
