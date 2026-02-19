---
last_updated: 2026-02-19T00:00:00Z
status: active
tier: platinum
---

# Personal AI Employee Dashboard

## System Status

| Component | Status | Notes |
|-----------|--------|-------|
| Cloud Agent | 🟢 Ready | Deploy to cloud VM |
| Local Agent | 🟢 Ready | Runs on your machine |
| Vault Sync | 🟢 Ready | Git-based sync |
| Agent Coordination | 🟢 Ready | Claim-by-move pattern |
| Health Monitoring | 🟢 Ready | Cloud health check |

## Platinum Tier Features

| Feature | Status |
|---------|--------|
| Cloud 24/7 Deployment | 🟢 Ready |
| Work-Zone Specialization | 🟢 Implemented |
| Vault Sync (Git) | 🟢 Ready |
| Agent Coordination | 🟢 Ready |
| Health Monitoring | 🟢 Ready |

## Architecture

### Cloud Agent (VM)
- **Owns:** Email triage, calendar, social drafts, scheduling
- **Location:** Oracle Cloud / AWS VM
- **Writes to:** /Updates/, /Pending_Approval/

### Local Agent (Your Machine)
- **Owns:** WhatsApp, payments, banking, approvals
- **Location:** Your computer
- **Reads from:** Cloud via Git sync
- **Merges:** Updates into Dashboard

## Security Rules

- Never sync secrets (.env, tokens, sessions)
- Only markdown/state files sync
- Cloud never stores payment credentials

## Deployment

### Cloud Setup
```bash
# Deploy to cloud
./cloud/cloud_setup.sh

# Deploy Odoo (optional)
./cloud/deploy_odoo.sh
```

### Local Setup
```bash
# Initialize Git sync
python scripts/vault_sync.py --vault ./vault --init git@github.com:you/repo.git

# Run local agent
python orchestrator.py --vault ./vault --dry-run
```

### Sync Schedule
```bash
# Cloud: push every 5 minutes
*/5 * * * * python scripts/vault_sync.py --vault ./vault --mode push

# Local: pull every 5 minutes
*/5 * * * * python scripts/vault_sync.py --vault ./vault --mode pull
```

---

*Last updated by AI Employee v0.4 (Platinum)*
