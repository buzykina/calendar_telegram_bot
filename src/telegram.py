import asyncio
import logging
import time

import httpx

from config import settings

logger = logging.getLogger(__name__)

_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
_CHAT_ID = int(settings.TELEGRAM_CHAT_ID)


async def send_approval_request(event: dict) -> bool:
    text = _format_message(event)
    sent_at = await _send_message(text)
    if sent_at is None:
        return False
    return await _poll_for_approval(after_timestamp=sent_at)


def _format_message(event: dict) -> str:
    lines = [
        "New calendar event detected — approve?",
        "",
        f"Title:    {event['title']}",
        f"Start:    {event['start_datetime']}",
        f"End:      {event.get('end_datetime') or 'N/A'}",
        f"Location: {event.get('location') or 'N/A'}",
        f"Notes:    {event.get('description') or 'N/A'}",
        "",
        "Reply YES to create or NO to skip.",
    ]
    return "\n".join(lines)


async def _send_message(text: str) -> int | None:
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                f"{_API}/sendMessage",
                json={"chat_id": _CHAT_ID, "text": text},
            )
            body = resp.json()
        except httpx.HTTPError as e:
            logger.error("Telegram sendMessage error: %s", e)
            return None

    if not body.get("ok"):
        logger.error("Telegram sendMessage failed: %s", body)
        return None

    sent_at: int = body["result"]["date"]
    return sent_at


async def _poll_for_approval(after_timestamp: int) -> bool:
    deadline = time.monotonic() + settings.APPROVAL_TIMEOUT_SECONDS
    offset: int | None = None

    async with httpx.AsyncClient() as client:
        while time.monotonic() < deadline:
            remaining = int(deadline - time.monotonic())
            poll_timeout = min(30, remaining)
            if poll_timeout <= 0:
                break

            params: dict = {
                "timeout": poll_timeout,
                "allowed_updates": ["message"],
            }
            if offset is not None:
                params["offset"] = offset

            try:
                resp = await client.get(
                    f"{_API}/getUpdates",
                    params=params,
                    timeout=poll_timeout + 5,
                )
                body = resp.json()
            except httpx.HTTPError as e:
                logger.warning("Telegram getUpdates error: %s", e)
                await asyncio.sleep(5)
                continue

            if not body.get("ok"):
                logger.warning("getUpdates non-ok: %s", body)
                await asyncio.sleep(5)
                continue

            for update in body.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                if msg.get("chat", {}).get("id") != _CHAT_ID:
                    continue
                if msg.get("date", 0) <= after_timestamp:
                    continue
                reply = msg.get("text", "").strip().upper()
                if reply == "YES":
                    return True
                if reply == "NO":
                    return False

    logger.warning("Approval timeout reached — event skipped")
    return False
