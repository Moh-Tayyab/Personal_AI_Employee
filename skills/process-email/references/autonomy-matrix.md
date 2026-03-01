# Autonomy Matrix Reference

Decision matrix for determining autonomy levels.

## Autonomy Levels

| Level | Name | Description |
|-------|------|-------------|
| 1 | Full Auto | Execute immediately, no notification |
| 2 | Notify | Execute and notify human |
| 3 | Requires Approval | Wait for human approval |

## Action Rules

| Action | Known Contact | New Contact |
|--------|---------------|-------------|
| Read email | Level 1 | Level 1 |
| Draft response | Level 1 | Level 1 |
| Send email | Level 2 | Level 3 |
| Create calendar | Level 2 | Level 3 |
| Make payment | Level 3 | Level 3 |

See `skills/reasoning/process-email/references/autonomy-matrix.md` for full matrix.