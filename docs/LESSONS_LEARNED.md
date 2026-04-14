# Architecture & Lessons Learned

**Project:** Personal AI Employee  
**Tier:** Gold (Autonomous Employee)  
**Status:** 94% Validated, Fully Operational  
**Date:** 2026-04-13  

---

## 🏗️ Architecture Decisions

### 1. Local-First, Cloud-Ready
- **Decision:** We chose a local-first architecture using Obsidian as the "Memory/GUI" and Python scripts as "Watchers".
- **Why:** Privacy is paramount for business data. By keeping the vault local, we ensure that sensitive emails, WhatsApp messages, and financial data never leave the user's machine unless explicitly sent via an MCP server.
- **Outcome:** Highly secure system. The `.env` file and vault are excluded from Git, ensuring secrets never leak.

### 2. File-Based Communication (The "Unix Way")
- **Decision:** Components communicate by moving Markdown files between folders (`Needs_Action` → `Plans` → `Approved` → `Done`).
- **Why:** This decouples the "Brain" (AI) from the "Senses" (Watchers) and "Hands" (MCPs). If the AI is down, watchers can still queue up tasks. If the AI is busy, watchers don't crash; they just drop files.
- **Outcome:** Extremely robust and debuggable. You can literally "see" what the AI is thinking by reading the files.

### 3. Multi-Provider AI System
- **Decision:** Implemented a fallback system using Groq (Llama 3.3) as the primary engine and Gemini/OpenRouter as backups.
- **Why:** Relying on a single API key is a single point of failure. Groq provides ultra-fast inference (500+ tokens/sec), ensuring the "Ralph Wiggum Loop" doesn't stall.
- **Outcome:** 94% Validation Score. The system is resilient to API quota exhaustion.

### 4. Human-in-the-Loop (HITL) via Approval Files
- **Decision:** Instead of asking the AI "Should I do this?", we force it to create an `APPROVAL_*.md` file that a human must move to `Approved/`.
- **Why:** AI can hallucinate. Sending a $5,000 invoice or a rude email by mistake is a catastrophic failure mode.
- **Outcome:** Safe deployment. The user retains 100% control over external actions.

---

## 🚧 Challenges & Solutions

### Challenge 1: Odoo Integration Complexity
- **Issue:** Odoo's API (JSON-RPC) requires specific payloads (e.g., `move_type` vs `type`, `action_post`). The AI often generated invalid payloads initially.
- **Solution:** We implemented a "Self-Healing" test suite. The system captures the error, feeds it back to the AI with context, and retries with a corrected payload.
- **Result:** Successfully created and posted invoices (`INV/2026/00002`) autonomously.

### Challenge 2: MCP Server Import Conflicts
- **Issue:** Python's `mcp` library (for Model Context Protocol) conflicted with our local `mcp/` folder.
- **Solution:** We renamed our local implementation to `mcp_local/` and updated imports. This allows us to use the official `mcp` SDK while keeping our custom servers isolated.
- **Result:** All 7 MCP servers now import and function correctly.

### Challenge 3: WhatsApp Session Persistence
- **Issue:** WhatsApp Web requires a QR scan every time the browser restarts.
- **Solution:** We used Playwright's `launch_persistent_context` with a dedicated `.whatsapp_session` directory.
- **Result:** The session persists across restarts, making the watcher truly "24/7".

---

## 💡 Key Learnings

1. **"Ralph Wiggum Loop" is Powerful but Dangerous:**
   - Letting the AI loop until "Done" is great for complex tasks, but without a `max_iterations` limit, it can burn through API quotas. We implemented a strict cap of 10 iterations.

2. **Structured Data > Free Text:**
   - Forcing the AI to output JSON or structured Markdown (with frontmatter) makes parsing much more reliable than asking it to "just reply".

3. **Dry Run is Essential:**
   - Developing with `DRY_RUN=true` saved us from accidentally spamming contacts or creating real invoices during testing.

4. **Odoo Online vs. Community:**
   - Odoo Online (SaaS) is easier to set up but has API limitations compared to a self-hosted Docker instance. For the hackathon, Odoo Online worked perfectly for invoicing and CRM.

---

## 🚀 Future Work (Platinum Tier)

- **Cloud Deployment:** Moving the "Watcher" and "Orchestrator" to a cloud VM for 24/7 uptime.
- **A2A Messaging:** Replacing file-based handoffs with direct Agent-to-Agent messaging for lower latency.
- **Banking Integration:** Adding Plaid or local bank APIs to the Finance Watcher for real-time balance monitoring.

---

*Documented by Muhammad Tayyab, Senior AI Engineer*
