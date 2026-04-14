# SKILL.md: Lead Qualification & Odoo CRM Update

**Version:** 1.0
**For:** CRM Digital FTE (Hackathon 5)

---

## 📋 Overview
This skill teaches the AI how to qualify a lead based on the BANT framework (Budget, Authority, Need, Timeline) and update Odoo CRM accordingly.

---

## 🔄 Workflow

### 1. Extract Information
When a new message arrives in `Needs_Action/`, extract:
- **Name:** (e.g., "John Doe")
- **Company:** (e.g., "Acme Corp")
- **Budget:** (e.g., "$5,000" or "Unknown")
- **Timeline:** (e.g., "ASAP", "Next Month")

### 2. Scoring Logic
- **Hot Lead:** Budget > $5,000 AND Timeline < 7 days.
- **Warm Lead:** Budget > $1,000 OR Timeline < 30 days.
- **Cold Lead:** Budget < $1,000 AND Timeline > 30 days.

### 3. Odoo CRM Actions
- **Hot:** Create `crm.lead` with `priority: High` and tag "Immediate Follow-up".
- **Warm:** Create `crm.lead` with `priority: Medium` and schedule follow-up in 24h.
- **Cold:** Create `crm.lead` with `priority: Low` and add to "Nurturing" pipeline.

### 4. Response Drafting
- **Hot:** "Thank you for your interest. I can have a proposal ready for you by EOD today. Shall I proceed?"
- **Warm:** "Thanks for reaching out! I'd love to learn more about your needs. Can we schedule a 15-min call?"
- **Cold:** "Thank you. I've added you to our newsletter for updates."

---

## ⚠️ Guardrails
1. **NEVER** fabricate a budget or timeline. If missing, ask the user.
2. **ALWAYS** use the `mcp_local/odoo/server.py` to create leads.
3. **LOG** the lead score and reasoning in the CRM FTE Audit Log.

---

## 🧪 Example Odoo Payload
```python
# Create a Hot Lead in Odoo
{
    "service": "object",
    "method": "execute_kw",
    "args": [
        "testing104", 2, "API_KEY", 
        "crm.lead", "create", 
        [{
            "name": "Acme Corp - Web Development",
            "partner_name": "John Doe",
            "email_from": "john@acme.com",
            "phone": "+1234567890",
            "priority": "3",
            "type": "opportunity",
            "description": "Budget: $5,000 | Timeline: ASAP | Score: HOT"
        }]
    ]
}
```
