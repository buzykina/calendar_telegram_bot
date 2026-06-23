import os
from dotenv import load_dotenv

load_dotenv("env/.env")


def _require(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


GEMINI_API_KEY: str = _require("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str = _require("TELEGRAM_CHAT_ID")

# Google OAuth 2.0 file paths
# credentials.json  — downloaded from Google Cloud Console (Desktop app type)
# token.json        — auto-created by scripts/get_oauth_token.py, auto-refreshed at runtime
GOOGLE_CREDENTIALS_FILE: str = os.environ.get("GOOGLE_CREDENTIALS_FILE", "env/credentials.json")
GOOGLE_TOKEN_FILE: str = os.environ.get("GOOGLE_TOKEN_FILE", "env/token.json")

# Official Google hosted MCP server endpoints
GMAIL_MCP_URL: str = "https://gmailmcp.googleapis.com/mcp/v1"
CALENDAR_MCP_URL: str = "https://calendarmcp.googleapis.com/mcp/v1"

EMAIL_LOOKBACK_MINUTES: int = int(os.environ.get("EMAIL_LOOKBACK_MINUTES", "30"))
APPROVAL_TIMEOUT_SECONDS: int = int(os.environ.get("APPROVAL_TIMEOUT_SECONDS", "300"))
