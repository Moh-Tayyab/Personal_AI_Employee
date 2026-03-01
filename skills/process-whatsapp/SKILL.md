---
name: process-whatsapp
description: |
  Processes incoming WhatsApp messages from Needs_Action folder, determines urgency,
  drafts appropriate responses, and creates actionable plans. Handles quick responses
  for time-sensitive WhatsApp communications.
allowed-tools: [Read, Write, Glob, Grep, Edit]
model: sonnet
---

# Process WhatsApp - Agent Skill

Analyzes and processes incoming WhatsApp messages with urgency detection, quick response drafting, and appropriate escalation for time-sensitive personal communications.

## When to Use

- New WhatsApp messages appear in `vault/Needs_Action/` (pattern: `WHATSAPP_*.md`)
- User commands: `/process-whatsapp`, "check WhatsApp", "process messages"
- Orchestrator triggers after WhatsApp watcher detection
- Urgent message handling

## Before Implementation

| Source | Gather |
|--------|--------|
| **Needs_Action/** | Scan for WHATSAPP_*.md files |
| **Company_Handbook.md** | Communication preferences, response templates |
| **Business_Goals.md** | Priority contacts, important relationships |
| **Done/** | Check for conversation history |

## Workflow

### Phase 1: Discovery
1. Scan `Needs_Action/` for `WHATSAPP_*.md` files
2. Read message metadata (sender, timestamp)
3. Check against priority contacts
4. Sort by timestamp (newest first)

### Phase 2: Analysis
For each message, analyze:
- **Sender:** Known contact, new contact, blocked
- **Urgency:** Time-sensitive keywords, after-hours message
- **Intent:** Question, update, request, greeting
- **Tone:** Casual, formal, urgent, emotional
- **Response Needed:** Yes/No, timeline

### Phase 3: Response Strategy
Determine response approach:

| Urgency | Response Time | Action |
|---------|---------------|--------|
| **URGENT** | Immediate | Draft response, request approval if needed |
| **HIGH** | Within 1 hour | Draft response, notify user |
| **NORMAL** | Within 4 hours | Draft response, batch with others |
| **LOW** | Within 24 hours | Draft when convenient |

### Phase 4: Action
1. Draft appropriate response
2. Create Plan.md if action required
3. Request approval for sensitive responses
4. Update Dashboard with status

## Urgency Detection

### URGENT Triggers
```yaml
urgent_keywords:
  - "emergency"
  - "urgent"
  - "asap"
  - "call me"
  - "need help now"
  - "where are you"
  - "are you ok"
  - "important"
  - "time sensitive"

urgent_patterns:
  - Multiple question marks
  - All caps words
  - After-hours from priority contact
  - Follow-up after no response
```

### Context-Based Urgency
```yaml
context_rules:
  - sender: family
    after_hours: urgent

  - sender: boss
    anytime: high

  - contains_question: true
    after_hours: high
    business_hours: normal

  - is_group_message: true
    default: low
```

## Response Tone Matching

```yaml
tone_detection:
  casual:
    indicators: ["hey", "hi", "yo", "sup", "lol", "haha"]
    response_style: casual, friendly, brief

  formal:
    indicators: ["dear", "sincerely", "please", "thank you"]
    response_style: professional, complete sentences

  urgent:
    indicators: ["asap", "urgent", "now", "immediately"]
    response_style: direct, action-focused

  emotional:
    indicators: ["!", "!!", "??", sad/angry emojis]
    response_style: empathetic, supportive
```

## WhatsApp Message Template

```markdown
---
message_id: WHATSAPP_<timestamp>_<id>
from: <sender_name_or_number>
from_type: contact|group|unknown
received: <timestamp>
priority: <urgency>
status: pending|processed
---

## Message
<original message content>

## Media
- [ ] Contains image
- [ ] Contains video
- [ ] Contains document
- [ ] Voice message

## Analysis
- **Sender:** <known/new contact>
- **Intent:** <question/update/request/greeting>
- **Tone:** <casual/formal/urgent/emotional>
- **Response Needed:** <yes/no>
- **Response Timeline:** <immediate/1h/4h/24h>

## Draft Response
<drafted response>

## Action Items
- [ ] <action 1>
- [ ] <action 2>
```

## Response Templates

### Quick Greeting
```
Hey! 👋 Thanks for reaching out. <response>
```

### Question Response
```
Hi! To answer your question: <answer>. Let me know if you need anything else!
```

### Urgent Acknowledgment
```
Got it! I'll <action> right away. Will update you soon.
```

### Follow-Up
```
Hey! Just following up on <topic>. <follow_up_message>
```

### Group Message
```
Thanks for the update! <brief acknowledgment>
```

## Error Handling

| Error | Recovery Action |
|-------|-----------------|
| Cannot parse message | Log error, flag for manual review |
| Unknown sender | Default to formal response, request approval |
| Media not accessible | Note in analysis, request manual review |
| Sensitive content detected | Flag for human review immediately |

## Security Considerations

### Never Do
- Share personal information without approval
- Auto-respond to unknown numbers with sensitive info
- Ignore urgent family messages
- Respond to suspicious links

### Always Do
- Check sender against known contacts
- Flag unknown senders for review
- Preserve message timestamps
- Log all processed messages

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Plan.md | `Plans/PLAN_<timestamp>_WHATSAPP_<id>.md` | Action plan |
| Draft Response | `Drafts/DRAFT_whatsapp_<id>.md` | Response draft |
| Processed Message | `Done/WHATSAPP_<id>.md` | Completed item |
| Audit Log | `Logs/<date>.json` | Processing log |

## Definition of Done

- [ ] All WHATSAPP_*.md files processed
- [ ] Urgency correctly assessed
- [ ] Responses drafted for messages needing reply
- [ ] Approval requests created for sensitive messages
- [ ] Dashboard updated with message count
- [ ] Processed messages moved to Done/

## Example Usage

```
User: /process-whatsapp

Claude: Found 4 new WhatsApp messages:

1. WHATSAPP_20260301_090000_mom.md (URGENT - family, after-hours)
2. WHATSAPP_20260301_091500_colleague.md (NORMAL - question)
3. WHATSAPP_20260301_093000_group.md (LOW - group update)
4. WHATSAPP_20260301_094500_unknown.md (NORMAL - unknown sender)

Processing in priority order...

[URGENT] Message from Mom: "Are you coming to dinner tonight?"
- Known contact, family priority
- Drafting quick response...

[HIGH] Draft response: "Yes! I'll be there at 7. See you soon! 🍝"
- Creating Plan.md for reminder
- Notification: Response drafted

[NORMAL] Colleague question - Drafting response
[LOW] Group update - Marking as read, no response needed
[REVIEW] Unknown sender - Creating approval request

Created:
- Plans/PLAN_20260301_WHATSAPP_mom.md
- Drafts/DRAFT_whatsapp_mom.md
- Pending_Approval/WHATSAPP_unknown_approval.md
- Done/WHATSAPP_group.md
```

## References

| File | Purpose |
|------|---------|
| `references/urgency-rules.md` | Urgency detection patterns |
| `references/response-templates.md` | Full response template library |
| `references/tone-matching.md` | Tone detection and matching rules |
| `references/whatsapp-contacts.md` | Known contacts and relationships |

---
*Version: 1.0.0 | Last Updated: 2026-03-01*