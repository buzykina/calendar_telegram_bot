# Email & Calendar Agent

A Python agent that watches your Gmail inbox, extracts calendar events using Gemini Flash, and asks for your approval via Telegram before adding anything to Google Calendar.

```
Gmail ──► Gemini Flash (extract event) ──► Calendar (duplicate check)
                                                     │
                                             Telegram (YES / NO)
                                                     │
                                           Calendar (create event)
```

---

## Stack

| Layer | Technology |
|---|---|
| LLM | Gemini Flash (`google-generativeai`) |
| Email + Calendar | Google MCP servers via `mcp` SDK |
| Approval | Telegram Bot (long-polling via `httpx`) |
| Auth | Google OAuth 2.0 (`credentials.json` + `token.json`) |

---

## Project structure

```
├── src/
│   ├── main.py             # pipeline orchestrator
│   ├── agent.py            # Gemini Flash — email → structured event
│   ├── mcp_client.py       # Gmail + Calendar MCP calls
│   └── telegram.py         # Telegram approval flow
├── config/
│   └── settings.py         # environment variable loading
├── scripts/
│   └── get_oauth_token.py  # one-time Google OAuth setup
├── env/
│   ├── .env                # secrets (gitignored)
│   ├── credentials.json    # OAuth desktop client (gitignored)
│   └── token.json          # auto-refreshed token (gitignored)
└── requirements.txt
```

---

## Setup

### 1. Google Cloud Console

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create or select a project
2. Enable **Gmail API** and **Google Calendar API**
3. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
4. Download the file and save it as `env/credentials.json`
5. Go to **OAuth consent screen → Test users** and add your Google account

### 2. Telegram bot

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
2. Start a chat with your bot, then open:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Copy the numeric `"id"` inside `"chat"` — that is your chat ID

### 3. Environment

```bash
cp .env.example env/.env
```

Fill in the three required values:

```env
GEMINI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 4. Install

```bash
pip install -r requirements.txt
```

### 5. Authorise Google (once)

```bash
python scripts/get_oauth_token.py
```

A browser window opens → log in with the Google account you want to use → `env/token.json` is saved. The token auto-refreshes on every run.

### 6. Run

```bash
python src/main.py
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | required | Gemini API key |
| `TELEGRAM_BOT_TOKEN` | required | Telegram bot token |
| `TELEGRAM_CHAT_ID` | required | Your Telegram chat ID |
| `EMAIL_LOOKBACK_MINUTES` | `30` | How far back to scan Gmail |
| `APPROVAL_TIMEOUT_SECONDS` | `300` | Seconds to wait for Telegram reply |
| `GOOGLE_CREDENTIALS_FILE` | `env/credentials.json` | Path to OAuth client file |
| `GOOGLE_TOKEN_FILE` | `env/token.json` | Path to token file |

---

## ⚠️ Known issue — MCP connectors not working

`mcp_client.py` connects to Google's hosted MCP servers (`gmailmcp.googleapis.com` and `calendarmcp.googleapis.com`) using the `mcp` Python SDK with Streamable HTTP transport.

In practice these return `200 Forbidden / "The caller does not have permission"` despite:
- A valid OAuth token
- Gmail API, Calendar API, and MCP services all enabled in Google Cloud
- The account added as a test user on the OAuth consent screen

The exact cause is unclear.
