# Claude Code Instructions

## Goal
Build a minimal email-to-calendar agent using MCP services.

The system should:
1. Fetch emails from the last X minutes via Gmail MCP
2. Detect if email contains a calendar event using LLM
3. Check if event already exists in Google Calendar via MCP
4. Ask user via Telegram if event should be created
5. Create event only after explicit approval

---

## STRICT ARCHITECTURE RULES

### 1. Simplicity first
- Keep the system minimal
- Do NOT introduce frameworks unless explicitly requested
- Avoid unnecessary abstractions

---

### 2. File responsibilities

- main.py:
  ONLY orchestrates flow logic. No API logic.

- agent.py:
  ONLY contains LLM logic (event extraction).

- mcp_client.py:
  ALL Gmail + Calendar MCP interactions MUST live here.

- telegram.py:
  ONLY handles Telegram messaging + responses.

- config/settings.py:
  ONLY environment variable access.

---

### 3. MCP rules
- All Gmail access MUST go through MCP client
- All Calendar access MUST go through MCP client
- Never call MCP directly from main.py or agent.py

---

### 4. LLM rules
- Always return structured JSON
- Never trust raw LLM output without validation
- If output is invalid → fail safely

---

### 5. Data handling
- Emails are treated as sensitive data
- Never log full email bodies
- Never print secrets or tokens

---

### 6. Workflow rule
The only valid pipeline is:

Gmail MCP → LLM agent → Calendar MCP → Telegram approval → Calendar MCP create

No shortcuts.

---

## Design philosophy
- minimal
- readable
- production-ready
- easy to extend