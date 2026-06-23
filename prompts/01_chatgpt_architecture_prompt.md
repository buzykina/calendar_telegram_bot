# ARCHITECTURE DESIGN PROMPT

You are designing a minimal production-ready AI agent system.

---

## Project Idea
Email-to-calendar agent using:
- Gmail MCP (email ingestion)
- Gemini Flash (event extraction)
- Google Calendar MCP (event validation + creation)
- Telegram (human approval)

---

## Constraints
- Keep architecture minimal
- No unnecessary frameworks
- Python-based system
- MCP required for external tools
- Must be production-minded but simple

---

## Required Output

### 1. Architecture Overview
- high-level diagram (text-based)

### 2. Components
- list modules + responsibilities

### 3. Data Flow
- step-by-step execution pipeline

### 4. MCP Strategy
- how MCP integrates into system cleanly

### 5. Failure Modes
- what can break + mitigation

### 6. MVP Plan
- smallest possible working version

### 7. Mental Model
- how to think about the system while coding

# 8. CLAUDE.md GENERATION (IMPORTANT)

Now generate a complete `CLAUDE.md` file for this project.

---

## Important
- Avoid overengineering
- Focus on clarity and implementation
- Keep system small and modular