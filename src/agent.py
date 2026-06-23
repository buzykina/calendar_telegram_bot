import json
import logging
import re

import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-1.5-flash")

_PROMPT = """\
Analyze the email below and extract calendar event information if present.

Return ONLY a JSON object with exactly these fields (no markdown, no explanation):
{{
  "is_event": true or false,
  "title": "event title or null",
  "start_datetime": "ISO 8601 datetime string or null",
  "end_datetime": "ISO 8601 datetime string or null",
  "location": "location string or null",
  "description": "brief description or null"
}}

Email subject: {subject}
Email body:
{body}
"""

_REQUIRED = {"is_event", "title", "start_datetime", "end_datetime"}
_JSON_RE = re.compile(r"\{[\s\S]*\}", re.MULTILINE)


def extract_event(email: dict) -> dict | None:
    subject = email.get("subject", "")
    body = email.get("body", email.get("snippet", ""))

    prompt = _PROMPT.format(subject=subject, body=body[:3000])
    try:
        response = _model.generate_content(prompt)
        raw = response.text.strip()
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return None

    match = _JSON_RE.search(raw)
    if not match:
        logger.warning("No JSON object found in LLM response")
        return None

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        logger.warning("LLM JSON parse failed: %s", e)
        return None

    if not _REQUIRED.issubset(data.keys()):
        logger.warning("LLM response missing required fields: %s", _REQUIRED - data.keys())
        return None

    if not data.get("is_event"):
        return None

    if not data.get("title") or not data.get("start_datetime"):
        logger.warning("Event missing title or start_datetime")
        return None

    return {
        "title": str(data["title"]),
        "start_datetime": str(data["start_datetime"]),
        "end_datetime": str(data["end_datetime"]) if data.get("end_datetime") else None,
        "location": str(data["location"]) if data.get("location") else None,
        "description": str(data["description"]) if data.get("description") else None,
    }
