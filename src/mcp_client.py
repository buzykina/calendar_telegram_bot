import base64
import json
import logging
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from config import settings

logger = logging.getLogger(__name__)

_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
]


def _get_access_token() -> str:
    creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_FILE, _SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(google.auth.transport.requests.Request())
        Path(settings.GOOGLE_TOKEN_FILE).write_text(creds.to_json())
    return creds.token


def _parse_content(result, fallback: Any) -> Any:
    if not result or not result.content:
        return fallback
    text = result.content[0].text
    try:
        return json.loads(text)
    except (json.JSONDecodeError, AttributeError):
        logger.warning("MCP result not valid JSON: %.120s", text)
        return fallback


# ── low-level client ──────────────────────────────────────────────────────────

class MCPClient:
    """Single reusable MCP session over Streamable HTTP."""

    def __init__(self, url: str, headers: dict[str, str]) -> None:
        self._url = url
        self._headers = headers
        self._session: ClientSession | None = None
        self._stack = AsyncExitStack()

    async def __aenter__(self) -> "MCPClient":
        read, write, _ = await self._stack.enter_async_context(
            streamablehttp_client(self._url, headers=self._headers)
        )
        self._session = await self._stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()
        return self

    async def __aexit__(self, *exc) -> None:
        await self._stack.aclose()

    async def call_tool(self, name: str, params: dict) -> Any:
        result = await self._session.call_tool(name, params)
        return _parse_content(result, fallback={})
    
    async def call_tool(self, name: str, params: dict) -> Any:
        result = await self._session.call_tool(name, params)
        return _parse_content(result, fallback={})
    
    async def list_tools(self) -> list:
        response = await self._session.list_tools()

        print("\n========== AVAILABLE MCP TOOLS ==========")
        for tool in response.tools:
            print(f"\nTool: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Input schema: {json.dumps(tool.inputSchema, indent=2)}")
            print("-" * 60)


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_get_access_token()}"}


# ── email helpers ─────────────────────────────────────────────────────────────

def _decode_base64(data: str) -> str:
    try:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_body(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return _decode_base64(data)
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    return ""


def _normalize_thread(thread: dict) -> dict:
    thread_id = thread.get("id", "unknown")
    snippet = thread.get("snippet", "")
    messages = thread.get("messages", [])
    if not messages:
        return {"id": thread_id, "subject": "", "body": snippet}
    payload = messages[0].get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
    return {
        "id": thread_id,
        "subject": headers.get("subject", ""),
        "body": _extract_body(payload) or snippet,
    }


# ── high-level clients ────────────────────────────────────────────────────────

class GmailMCPClient:
    async def fetch_recent_emails(self, lookback_minutes: int) -> list[dict]:
        async with MCPClient(settings.GMAIL_MCP_URL, _auth_headers()) as gmail:
            data = await gmail.call_tool(
                "search_threads",
                {"query": f"newer_than:{lookback_minutes}m", "pageSize": 20},
            )
            threads = data.get("threads", data) if isinstance(data, dict) else data
            if not isinstance(threads, list):
                return []

            emails: list[dict] = []
            for thread in threads[:10]:
                thread_id = thread.get("id") or thread.get("threadId")
                if not thread_id:
                    continue
                detail = await gmail.call_tool("get_thread", {"threadId": thread_id})
                if isinstance(detail, dict):
                    emails.append(_normalize_thread(detail))
            return emails


class CalendarMCPClient:
    async def all_events(self) -> list[dict]:
        async with MCPClient(settings.CALENDAR_MCP_URL, _auth_headers()) as calendar:
            events = await calendar.call_tool("list_events", {"calendarId": "primary"})
            return events

    async def event_exists(self, title: str, start_time: str) -> bool:
        async with MCPClient(settings.CALENDAR_MCP_URL, _auth_headers()) as calendar:
            data = await calendar.call_tool(
                "list_events",
                {
                    "calendarId": "primary",
                    "startTime": start_time,
                    "fullText": title,
                    "pageSize": 5,
                },
            )
            events = data.get("items", data) if isinstance(data, dict) else data
            if not isinstance(events, list):
                return False
            return any(e.get("summary", "").lower() == title.lower() for e in events)

    async def create_event(self, event_data: dict) -> dict:
        async with MCPClient(settings.CALENDAR_MCP_URL, _auth_headers()) as calendar:
            return await calendar.call_tool("create_event", event_data)
