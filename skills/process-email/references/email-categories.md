# Email Categories Reference

Detailed category detection rules for email classification.

## Primary Categories

| Category | Keywords | Priority | Autonomy |
|----------|----------|----------|----------|
| `invoice` | invoice, bill, payment, receipt | HIGH | Level 2 |
| `meeting` | meeting, schedule, call, zoom | NORMAL | Level 2 |
| `support` | help, issue, problem, bug | HIGH | Level 2 |
| `sales` | proposal, quote, interested | HIGH | Level 3 |
| `personal` | family, friend, personal | NORMAL | Level 2 |
| `legal` | legal, attorney, contract | URGENT | Level 3 |
| `spam` | unsubscribe, promotional | LOW | Level 1 |

## Detection Patterns

See `skills/reasoning/process-email/references/email-categories.md` for full patterns.