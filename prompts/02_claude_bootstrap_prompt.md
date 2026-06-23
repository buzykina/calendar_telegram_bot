You are building a COMPLETE but MINIMAL production-ready Python system.

# PROJECT
Email-to-calendar agent using:
- Gmail MCP (fetch emails)
- Gemini Flash (event extraction)
- Google Calendar MCP (check + create events)
- Telegram bot (approval step)

---

# CRITICAL CONSTRAINTS
- System must be fully runnable (no pseudo-code)
- MCP calls must be clearly abstracted in mcp_client.py
- No missing functions allowed
- No placeholder comments like "implement later"
- Keep code minimal but functional
- Use Python only

---

# REQUIRED OUTPUT FORMAT

Generate the FULL PROJECT with:

## 1. File tree

## 2. FULL CODE for EACH FILE:
- main.py
- agent.py
- mcp_client.py
- telegram.py
- config/settings.py
- requirements.txt

## 3. Brief explanation of execution flow

---

# SAFETY RULES
- Never access .env directly in code
- Always use config/settings.py
- LLM output must be validated JSON
- Fail safely on invalid data

---

# IMPORTANT
This is NOT a design exercise.
This must be a working system with complete implementations.