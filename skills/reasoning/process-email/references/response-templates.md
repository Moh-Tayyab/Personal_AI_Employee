# Response Templates Library

## Invoice/Payment Templates

### Invoice Received - Acknowledgment

```markdown
Subject: Re: Invoice #{invoice_number}

Dear {sender_name},

Thank you for sending invoice #{invoice_number} for {amount}.

I have received this invoice and will process it according to our standard
payment terms. You can expect payment by {expected_date}.

If you have any questions, please don't hesitate to reach out.

Best regards,
{signature}
```

### Invoice Received - Question

```markdown
Subject: Re: Invoice #{invoice_number} - Clarification Needed

Dear {sender_name},

Thank you for sending invoice #{invoice_number}.

I have reviewed the invoice and have a question regarding:
- {specific_item_in_question}

Could you please provide clarification on this item?

Once resolved, I will process the payment promptly.

Best regards,
{signature}
```

### Payment Confirmation

```markdown
Subject: Payment Confirmation - Invoice #{invoice_number}

Dear {sender_name},

This email confirms that payment of {amount} for invoice #{invoice_number}
has been processed.

Transaction details:
- Amount: {amount}
- Date: {payment_date}
- Reference: {transaction_reference}
- Method: {payment_method}

Please allow 2-3 business days for the payment to reflect in your account.

Best regards,
{signature}
```

### Payment Overdue Notice Response

```markdown
Subject: Re: Overdue Payment Reminder

Dear {sender_name},

Thank you for bringing this to my attention.

I apologize for the delay in payment. I have now processed the payment
for invoice #{invoice_number}.

{if_payment_sent}
Transaction details:
- Amount: {amount}
- Date: {payment_date}
- Reference: {transaction_reference}
{endif}

I sincerely apologize for any inconvenience this delay may have caused.

Best regards,
{signature}
```

## Meeting/Scheduling Templates

### Meeting Request - Accept

```markdown
Subject: Re: Meeting Request - Confirmed

Dear {sender_name},

Thank you for the meeting request. I'm happy to confirm the following:

Date: {meeting_date}
Time: {meeting_time}
Duration: {duration}
Location/Link: {meeting_link}

I look forward to our discussion.

Best regards,
{signature}
```

### Meeting Request - Propose Alternative

```markdown
Subject: Re: Meeting Request - Alternative Time

Dear {sender_name},

Thank you for reaching out to schedule a meeting.

Unfortunately, I'm not available at the proposed time. However, I'm
available during the following times:

{alternative_1}: {date} at {time}
{alternative_2}: {date} at {time}
{alternative_3}: {date} at {time}

Please let me know which works best for you, or feel free to suggest
another time that fits your schedule.

Best regards,
{signature}
```

### Meeting Request - Decline

```markdown
Subject: Re: Meeting Request

Dear {sender_name},

Thank you for thinking of me for this meeting.

Unfortunately, I'm unable to attend due to {reason}. However, I'd be
happy to {alternative_arrangement}.

If there's anything specific you'd like me to provide or address before
the meeting, please let me know.

Best regards,
{signature}
```

### Meeting Reminder

```markdown
Subject: Reminder: Meeting Tomorrow - {meeting_title}

Dear {sender_name},

This is a friendly reminder about our meeting tomorrow:

Date: {meeting_date}
Time: {meeting_time}
Duration: {duration}
Location/Link: {meeting_link}

Agenda:
{agenda_items}

Please let me know if anything has changed or if you have any questions.

Best regards,
{signature}
```

## Support Templates

### Support Request - Acknowledgment

```markdown
Subject: Re: Support Request #{ticket_number}

Dear {sender_name},

Thank you for reaching out. I've received your support request and
understand you're experiencing {issue_summary}.

I've assigned this case a priority level of {priority} and will work
to resolve it as quickly as possible.

Expected response time: {response_time}

In the meantime, if you have any additional information that might help,
please don't hesitate to share it.

Best regards,
{signature}
```

### Support Request - Resolution

```markdown
Subject: Re: Support Request #{ticket_number} - Resolved

Dear {sender_name},

I'm pleased to inform you that the issue with {issue_summary} has been
resolved.

**Resolution:**
{resolution_details}

**Steps taken:**
{steps_taken}

Please verify that everything is working as expected. If you encounter
any further issues, please reply to this email and I'll be happy to help.

Best regards,
{signature}
```

### Support Request - Need More Information

```markdown
Subject: Re: Support Request #{ticket_number} - Information Needed

Dear {sender_name},

Thank you for your patience while I investigate your issue.

To help me resolve this more effectively, could you please provide:

1. {information_needed_1}
2. {information_needed_2}
3. {information_needed_3}

{if_applicable}
It would also be helpful if you could:
- {additional_request}
{endif}

Once I have this information, I'll be able to proceed with resolving
your issue.

Best regards,
{signature}
```

## Sales Templates

### Quote Request - Response

```markdown
Subject: Re: Quote Request - {product/service}

Dear {sender_name},

Thank you for your interest in {product/service}.

I'm pleased to provide you with the following quote:

{quote_details}

This quote is valid for {validity_period} days.

If you have any questions or would like to discuss this further, I'm
happy to schedule a call at your convenience.

Best regards,
{signature}
```

### Demo Request - Scheduling

```markdown
Subject: Re: Demo Request - Scheduling

Dear {sender_name},

Thank you for your interest in seeing {product/service} in action!

I'd be happy to schedule a personalized demo for you. Please let me
know your availability for the following dates:

{date_option_1}: {time_slots}
{date_option_2}: {time_slots}
{date_option_3}: {time_slots}

The demo will typically last about {duration} and will cover:
{demo_agenda}

Looking forward to showing you what {product/service} can do!

Best regards,
{signature}
```

### Lead Follow-up

```markdown
Subject: Following Up on Our Conversation

Dear {sender_name},

I hope this email finds you well. I wanted to follow up on our recent
conversation about {topic}.

As discussed, here are the key points:
{key_points_discussed}

{next_steps}

Please let me know if you have any questions or if there's anything
else I can help with.

Best regards,
{signature}
```

## Personal Templates

### Thank You Response

```markdown
Subject: Re: {original_subject}

Dear {sender_name},

Thank you so much for your kind {message_type}. It means a lot to me.

{personal_response}

Looking forward to {future_reference}.

Warm regards,
{signature}
```

### Congratulations Response

```markdown
Subject: Re: Congratulations!

Dear {sender_name},

Thank you so much for your thoughtful message!

{personal_response}

I'm excited about {achievement} and grateful for your support.

Warm regards,
{signature}
```

## Legal Templates (DRAFT ONLY - Always Requires Approval)

### Legal Notice Acknowledgment (DRAFT)

```markdown
Subject: Re: {legal_subject} - Acknowledgment of Receipt

Dear {sender_name},

This email acknowledges receipt of your correspondence dated {date}
regarding {subject}.

I am reviewing the matter carefully and will respond substantively
within {response_deadline}.

{if_appropriate}
In the meantime, I have forwarded this matter to my legal counsel for
review.
{endif}

This correspondence is without prejudice to any rights or defenses.

Sincerely,
{signature}

LEGAL DISCLAIMER: This email does not constitute legal advice and
should not be relied upon as such. All rights reserved.
```

## Spam/Newsletter Templates

### Unsubscribe Request

```markdown
Subject: Unsubscribe Request

To Whom It May Concern,

Please remove the following email address from your mailing list:
{email_address}

Thank you.
```

## Template Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{sender_name}` | Recipient's name | John Doe |
| `{invoice_number}` | Invoice reference | INV-2024-001 |
| `{amount}` | Monetary amount | $500.00 |
| `{meeting_date}` | Meeting date | March 15, 2026 |
| `{meeting_time}` | Meeting time | 2:00 PM EST |
| `{duration}` | Meeting duration | 30 minutes |
| `{meeting_link}` | Video call URL | zoom.us/j/xxx |
| `{signature}` | Email signature | John Smith\nCEO |
| `{ticket_number}` | Support ticket ID | SUP-12345 |
| `{priority}` | Priority level | High |
| `{response_time}` | Expected response | 24 hours |

## Tone Guidelines

### Formal Tone
Use for: Legal, first business contact, senior executives
- "Dear [Name],"
- Complete sentences
- No contractions
- Professional closing

### Professional Tone
Use for: Standard business, clients, colleagues
- "Hi [Name],"
- Complete sentences with some contractions
- Clear and direct
- Friendly professional closing

### Casual Tone
Use for: Known contacts, ongoing relationships
- "Hi [Name]," or just "[Name],"
- Conversational style
- Contractions acceptable
- Warm closing