#!/usr/bin/env python3
"""Exchange Mail MCP Server - Microsoft 365 Graph API via Device Code Flow"""

import msal
import requests
import json
import os
import sys
from mcp.server.fastmcp import FastMCP

CLIENT_ID = os.environ.get("MS_CLIENT_ID", "14d82eec-204b-4c2f-b7e8-296a70dab67e")
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["https://graph.microsoft.com/Mail.Read"]
TOKEN_CACHE_FILE = os.environ.get("MS_TOKEN_CACHE", os.path.expanduser("~/.ms_token_cache.json"))
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

mcp = FastMCP("exchange-mail")


def _get_token() -> str:
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE) as f:
            cache.deserialize(f.read())

    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            if cache.has_state_changed:
                with open(TOKEN_CACHE_FILE, "w") as f:
                    f.write(cache.serialize())
            return result["access_token"]

    # No cached token - try device code flow if running interactively
    if sys.stdin.isatty():
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Device flow failed: {flow}")
        print(f"\nLogin required:", file=sys.stderr)
        print(f"  1. Open https://login.microsoft.com/device", file=sys.stderr)
        print(f"  2. Enter code: {flow['user_code']}", file=sys.stderr)
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            with open(TOKEN_CACHE_FILE, "w") as f:
                f.write(cache.serialize())
            return result["access_token"]

    raise RuntimeError(
        "Exchange token expired. Run `exchange-mail-auth` in terminal to re-authenticate."
    )


def _headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}"}


@mcp.tool()
def check_exchange_mail(count: int = 10) -> str:
    """Check recent Exchange emails (ho.shin@teoul.com). Returns subject, sender, date."""
    url = f"{GRAPH_BASE}/me/mailFolders/inbox/messages?$top={count}&$orderby=receivedDateTime desc"
    resp = requests.get(url, headers=_headers())
    if resp.status_code != 200:
        return f"Error {resp.status_code}: {resp.text}"

    messages = resp.json().get("value", [])
    if not messages:
        return "No messages found."

    lines = []
    for i, msg in enumerate(messages, 1):
        sender = msg.get("from", {}).get("emailAddress", {})
        dt = msg.get("receivedDateTime", "")[:16].replace("T", " ")
        read = "" if msg.get("isRead") else " [NEW]"
        lines.append(
            f"[{i}] {dt}{read}\n"
            f"  From: {sender.get('name', '')} <{sender.get('address', '')}>\n"
            f"  Subject: {msg.get('subject', '')}"
        )
    return "\n\n".join(lines)


@mcp.tool()
def read_exchange_mail(message_id: str) -> str:
    """Read full content of a specific Exchange email by message ID."""
    url = f"{GRAPH_BASE}/me/messages/{message_id}?$select=subject,from,toRecipients,receivedDateTime,body"
    resp = requests.get(url, headers=_headers())
    if resp.status_code != 200:
        return f"Error {resp.status_code}: {resp.text}"

    msg = resp.json()
    sender = msg.get("from", {}).get("emailAddress", {})
    to_list = ", ".join(
        r.get("emailAddress", {}).get("address", "") for r in msg.get("toRecipients", [])
    )
    body = msg.get("body", {}).get("content", "")

    return (
        f"Subject: {msg.get('subject', '')}\n"
        f"From: {sender.get('name', '')} <{sender.get('address', '')}>\n"
        f"To: {to_list}\n"
        f"Date: {msg.get('receivedDateTime', '')[:16].replace('T', ' ')}\n"
        f"---\n{body}"
    )


@mcp.tool()
def search_exchange_mail(query: str, count: int = 10) -> str:
    """Search Exchange emails by keyword. Searches subject and body."""
    url = (
        f"{GRAPH_BASE}/me/messages?$search=\"{query}\""
        f"&$top={count}&$orderby=receivedDateTime desc"
        f"&$select=id,subject,from,receivedDateTime,isRead"
    )
    resp = requests.get(url, headers=_headers())
    if resp.status_code != 200:
        return f"Error {resp.status_code}: {resp.text}"

    messages = resp.json().get("value", [])
    if not messages:
        return f"No results for '{query}'."

    lines = []
    for i, msg in enumerate(messages, 1):
        sender = msg.get("from", {}).get("emailAddress", {})
        dt = msg.get("receivedDateTime", "")[:16].replace("T", " ")
        lines.append(
            f"[{i}] {dt}\n"
            f"  From: {sender.get('name', '')} <{sender.get('address', '')}>\n"
            f"  Subject: {msg.get('subject', '')}\n"
            f"  ID: {msg.get('id', '')}"
        )
    return "\n\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
