"""
Run this ONCE to authorise the agent with your Google account.

Usage:
    python scripts/get_oauth_token.py

Reads  env/credentials.json  (downloaded from Google Cloud Console).
Writes env/token.json         (used at runtime; auto-refreshed automatically).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
    "https://www.googleapis.com/auth/gmail.compose"
]

CREDENTIALS_FILE = Path("env/credentials.json")
TOKEN_FILE = Path("env/token.json")


def main() -> None:
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: {CREDENTIALS_FILE} not found.")
        print("Download it from Google Cloud Console → APIs & Services → Credentials.")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    TOKEN_FILE.write_text(creds.to_json())
    print(f"\nDone — {TOKEN_FILE} saved. You can now run the agent.")


if __name__ == "__main__":
    main()
