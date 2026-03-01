# Email Category Detection Rules

## Primary Categories

### 1. Invoice/Payment (`invoice`)

**Trigger Keywords:**
- invoice, bill, payment, receipt, due, overdue
- amount, total, subtotal, tax, fee
- invoice #, invoice number, ref #
- bank details, wire transfer, payment method

**Detection Pattern:**
```python
INVOICE_PATTERNS = [
    r'invoice\s*[#:]?\s*\d+',
    r'total\s*(amount|due)',
    r'payment\s*(due|received|overdue)',
    r'bill\s*(for|to)',
    r'\$\d+(\.\d{2})?',  # Currency amounts
]
```

**Sub-categories:**
- `invoice_received` - New invoice to pay
- `invoice_sent` - Confirmation of sent invoice
- `payment_received` - Payment confirmation
- `payment_overdue` - Overdue notice
- `payment_reminder` - Payment reminder

### 2. Meeting/Scheduling (`meeting`)

**Trigger Keywords:**
- meeting, call, zoom, teams, google meet
- schedule, calendar, appointment
- available, availability, time slot
- reschedule, cancel, postpone
- agenda, minutes, follow-up

**Detection Pattern:**
```python
MEETING_PATTERNS = [
    r'(schedule|set up|arrange)\s*(a|an)?\s*meeting',
    r'(zoom|teams|google meet|video call)',
    r'available\s*(on|at|for)',
    r'(monday|tuesday|wednesday|thursday|friday)\s*(at|@)',
    r'\d{1,2}(:\d{2})?\s*(am|pm|AM|PM)',
]
```

**Sub-categories:**
- `meeting_request` - New meeting request
- `meeting_confirmation` - Confirmed meeting
- `meeting_reschedule` - Reschedule request
- `meeting_cancel` - Cancellation
- `meeting_reminder` - Upcoming reminder

### 3. Support/Issues (`support`)

**Trigger Keywords:**
- help, issue, problem, error, bug
- not working, broken, failed, crash
- support, assistance, urgent
- can't access, locked out, reset

**Detection Pattern:**
```python
SUPPORT_PATTERNS = [
    r'(need|require)\s*(help|assistance|support)',
    r'(not working|broken|failed|error)',
    r'(can\'?t|cannot)\s*(access|login|connect)',
    r'(bug|issue|problem)\s*(report|with)?',
    r'urgent\s*(help|assistance|issue)',
]
```

**Sub-categories:**
- `support_ticket` - New support ticket
- `bug_report` - Bug report
- `access_issue` - Access/login problem
- `feature_request` - Feature request
- `urgent_support` - Urgent issue

### 4. Sales/Business (`sales`)

**Trigger Keywords:**
- proposal, quote, pricing, interested
- demo, trial, subscription
- partnership, collaboration, opportunity
- contract, agreement, terms

**Detection Pattern:**
```python
SALES_PATTERNS = [
    r'(send|provide)\s*(a|an)?\s*(quote|proposal)',
    r'(interested|looking for|considering)',
    r'(pricing|price|cost|budget)',
    r'(demo|trial|pilot)',
    r'(partnership|collaboration|opportunity)',
]
```

**Sub-categories:**
- `lead_inquiry` - New lead inquiry
- `quote_request` - Quote request
- `demo_request` - Demo request
- `partnership` - Partnership inquiry
- `proposal_followup` - Proposal follow-up

### 5. Personal (`personal`)

**Trigger Keywords:**
- personal, family, friend
- birthday, anniversary, congratulations
- thank you, appreciation, gratitude
- casual greetings from known contacts

**Detection Pattern:**
```python
PERSONAL_PATTERNS = [
    r'(happy|congratulations|best wishes)',
    r'(thank you|thanks|appreciate)',
    r'(family|personal|private)',
    r'(birthday|anniversary|celebration)',
]
```

**Sub-categories:**
- `personal_greeting` - Personal greeting
- `thank_you` - Thank you message
- `congratulations` - Congratulations
- `personal_request` - Personal favor/request

### 6. Legal (`legal`)

**Trigger Keywords:**
- legal, attorney, lawyer, counsel
- contract, agreement, terms, conditions
- lawsuit, litigation, settlement
- intellectual property, copyright, trademark
- cease and desist, notice, violation

**Detection Pattern:**
```python
LEGAL_PATTERNS = [
    r'(legal|attorney|lawyer|counsel)',
    r'(contract|agreement|terms|conditions)',
    r'(lawsuit|litigation|settlement)',
    r'(cease and desist|violation|infringement)',
    r'(intellectual property|copyright|trademark)',
]
```

**Sub-categories:**
- `legal_notice` - Legal notice
- `contract_review` - Contract for review
- `legal_threat` - Legal threat/warning
- `nda` - NDA request
- `terms_update` - Terms update

**Special Handling:**
- ALWAYS set to Level 3 (requires approval)
- ALWAYS flag for human review
- NEVER auto-respond to legal matters
- Preserve all original content

### 7. Spam/Marketing (`spam`)

**Trigger Keywords:**
- unsubscribe, promotional, newsletter
- limited time, act now, special offer
- click here, buy now, free trial
- marketing emails from unknown senders

**Detection Pattern:**
```python
SPAM_PATTERNS = [
    r'unsubscribe',
    r'(limited time|act now|special offer)',
    r'(click here|buy now|free trial)',
    r'(promotional|newsletter|marketing)',
    r'no-reply@|noreply@',
]
```

**Sub-categories:**
- `newsletter` - Newsletter subscription
- `promotional` - Marketing promotion
- `spam` - Clear spam
- `subscription` - Subscription notification

**Special Handling:**
- Can be auto-archived (Level 1)
- Do not auto-respond
- Log for subscription audit

## Multi-Category Handling

When an email matches multiple categories:

1. **Priority Order:** legal > invoice > meeting > support > sales > personal > spam
2. **Combine flags:** Mark all matched categories
3. **Use highest priority category** for action determination

```yaml
# Example: Legal invoice
categories: [legal, invoice]
primary_category: legal  # Higher priority
requires_approval: true  # Legal always requires approval
```

## Confidence Scoring

Each category match includes a confidence score:

```yaml
category: invoice
confidence: 0.95
matched_patterns:
  - "invoice #1234" (0.9)
  - "total due: $500" (0.85)
  - "payment due date" (0.8)
```

**Confidence Thresholds:**
- `> 0.8`: High confidence - proceed with category
- `0.5 - 0.8`: Medium - flag for review
- `< 0.5`: Low - mark as `uncategorized`, manual review

## Sender-Based Category Override

Known contacts can override category detection:

```yaml
# In Business_Goals.md or Contacts.md
priority_contacts:
  - email: boss@company.com
    default_category: high_priority
    always_respond: true

  - email: legal@lawfirm.com
    always_level_3: true
    category: legal

ignored_senders:
  - email: newsletter@spam.com
    auto_category: spam
    auto_archive: true
```