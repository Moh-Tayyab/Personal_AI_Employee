# Approval Request Templates

## Payment Approval Request

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

# Payment Approval Required

## Details
- **Amount:** $500.00
- **To:** Client A (Bank: XXXX1234)
- **Reference:** Invoice #1234

## Reason
Payment for services rendered.

## Actions
- To **approve**: Move this file to the /Approved folder
- To **reject**: Move this file to the /Rejected folder

## Note
NEVER auto-approve payments. Always require human approval.
```

## Email Send Approval Request

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice for January 2026
created: 2026-01-07T10:30:00Z
status: pending
---

# Email Approval Required

## Email Details
- **To:** client@example.com
- **Subject:** Invoice for January 2026
- **Attachment:** /Vault/Invoices/2026-01_Client_A.pdf

## Preview
Please find attached your invoice for January 2026.

## Actions
- To **approve**: Move this file to the /Approved folder
- To **reject**: Move this file to the /Rejected folder
```

## Social Media Post Approval Request

```markdown
---
type: approval_request
action: social_post
platform: linkedin
content: "Excited to announce our new product launch..."
scheduled_time: 2026-01-07T14:00:00Z
created: 2026-01-07T10:30:00Z
status: pending
---

# Social Media Post Approval

## Platform
LinkedIn

## Content
Excited to announce our new product launch! We've been working hard to bring you something special. Stay tuned for more details!

## Scheduled Time
January 7, 2026 at 2:00 PM

## Actions
- To **approve**: Move this file to the /Approved folder
- To **reject**: Move this file to the /Rejected folder

## Note
New contacts/replies require approval. Scheduled posts may be auto-approved if within policy.
```
