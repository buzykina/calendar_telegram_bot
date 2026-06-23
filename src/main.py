import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from agent import extract_event
from mcp_client import GmailMCPClient, CalendarMCPClient
from telegram import send_approval_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def run() -> None:
    gmail = GmailMCPClient()
    calendar = CalendarMCPClient()

    logger.info("Fetching emails from the last %d minutes", settings.EMAIL_LOOKBACK_MINUTES)
    emails = await gmail.fetch_recent_emails(settings.EMAIL_LOOKBACK_MINUTES)
    logger.info("Found %d emails to process", len(emails))

    for email in emails:
        email_id = email.get("id", "unknown")
        logger.info("Processing email id=%s", email_id)

        event = extract_event(email)
        if event is None:
            logger.info("Email id=%s: no calendar event detected", email_id)
            continue

        logger.info("Event detected: '%s' at %s", event["title"], event["start_datetime"])

        already_exists = await calendar.event_exists(event["title"], event["start_datetime"])
        if already_exists:
            logger.info("Event '%s' already in calendar — skipping", event["title"])
            continue

        approved = await send_approval_request(event)
        if not approved:
            logger.info("Event '%s' not approved — skipping", event["title"])
            continue

        created = await calendar.create_event({
            "summary": event["title"],
            "startTime": event["start_datetime"],
            "endTime": event["end_datetime"] or event["start_datetime"],
            "location": event.get("location") or "",
            "description": event.get("description") or "",
        })
        logger.info("Event created — id=%s", created.get("id", "unknown"))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
