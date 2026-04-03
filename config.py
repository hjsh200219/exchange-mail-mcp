"""Shared configuration for Exchange Mail MCP."""

import os

CLIENT_ID = os.environ.get("MS_CLIENT_ID", "14d82eec-204b-4c2f-b7e8-296a70dab67e")
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["https://graph.microsoft.com/Mail.Read"]
TOKEN_CACHE_FILE = os.environ.get("MS_TOKEN_CACHE", os.path.expanduser("~/.ms_token_cache.json"))
