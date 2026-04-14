# Personal AI Employee - Gold Tier Implementation

> **Digital FTE (Full-Time Equivalent)** - Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

[![Gold Tier](https://img.shields.io/badge/Tier-Gold-brightgreen)](docs/GOLD_TIER_CHECKLIST.md)
[![Validation](https://img.shields.io/badge/Validation-88%25-brightgreen)](demo/validate_gold_tier.py)
[![Tests](https://img.shields.io/badge/Tests-17%20files-blue)](tests/)
[![MCP Servers](https://img.shields.io/badge/MCP%20Servers-7-orange)](mcp/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for Odoo)
- Obsidian (optional, for vault viewing)

### 5-Minute Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Personal_AI_Employee

# 2. Setup Python environment
./scripts/setup_venv.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys (see docs/)

# 4. Validate installation
python demo/validate_gold_tier.py --vault ./vault

# 5. Run integration test
python demo/simple_integration_test.py
```

### Start AI Employee

```bash
# Activate virtual environment
source .venv/bin/activate

# Start orchestrator (main brain)
python orchestrator.py --vault ./vault

# Or start with PM2 for 24/7 operation
pm2 start ecosystem.config.js
pm2 save
```

---

## 📊 Gold Tier Status

**Completion: 85%** | **Validation Score: 88%** (45/51 checks, 0 failures)

| Feature | Status | Details |
|---------|--------|---------|
| Multiple Watchers | ✅ | Gmail, WhatsApp, Filesystem |
| Plan.md Generation | ✅ | Automatic for each task |
| Email MCP | ✅ | Send, search, mark as read |
| LinkedIn MCP | ✅ | Post, business updates |
| Twitter MCP | ✅ | Tweets, threads, search |
| Facebook/Instagram MCP | ✅ | Cross-platform posting |
| Odoo Accounting | ✅ | Invoices, payments, reports |
| Approval Workflow | ✅ | File-based HITL system |
| CEO Briefing | ✅ | Weekly autonomous audit |
| Ralph Wiggum Loop | ✅ | Persistence pattern |
| Error Recovery | ✅ | Circuit breakers, retry |
| Audit Logging | ✅ | Daily JSON logs |

**Remaining for 100%:**
- [ ] API keys configured (LinkedIn, Twitter, Facebook)
- [ ] Odoo Docker setup completed
- [ ] WhatsApp Web login tested
- [ ] Demo video recorded (5-10 min)
- [ ] Hackathon submission form filled

See: [Gold Tier Checklist](docs/GOLD_TIER_CHECKLIST.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│   Gmail API  │  WhatsApp Web  │  File System  │  Odoo ERP  │
│   LinkedIn   │  Twitter API   │  Meta Graph   │  Bank API  │
└────────┬────────────┬──────────────┬──────────────┬─────────┘
         │            │              │              │
         ▼            ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│  PERCEPTION LAYER — Watchers (Python scripts, 24/7)         │
│  GmailWatcher │ WhatsAppWatcher │ FilesystemWatcher         │
└────────────────────────┬────────────────────────────────────┘
                         ▼ (creates .md files)
┌─────────────────────────────────────────────────────────────┐
│  MEMORY LAYER — Obsidian Vault (Local Markdown Database)    │
│  /Needs_Action/ │ /Plans/ │ /Approved/ │ /Done/ │ /Logs/    │
│  Dashboard.md │ Company_Handbook.md │ Business_Goals.md      │
└────────────────────────┬────────────────────────────────────┘
                         ▼ (reads files, writes plans)
┌─────────────────────────────────────────────────────────────┐
│  REASONING LAYER — Orchestrator + Multi-Provider AI         │
│  Orchestrator.py: Detects, Plans, Triggers AI, Executes     │
│  AI Providers: Qwen Code, Claude, Gemini, OpenRouter        │
│  Ralph Wiggum Loop: Keeps AI working until task complete    │
└────────────────────────┬────────────────────────────────────┘
                         ▼ (calls MCP servers)
┌─────────────────────────────────────────────────────────────┐
│  ACTION LAYER — MCP Servers (Model Context Protocol)        │
│  7 Servers, 49 Tools:                                       │
│  Email │ Filesystem │ Approval │ LinkedIn │ Twitter │ Social│
│  Odoo Accounting Integration                                │
└────────────────────────┬────────────────────────────────────┘
                         ▼ (human approval gate)
┌─────────────────────────────────────────────────────────────┐
│  HUMAN-IN-THE-LOOP — Approval Workflow                      │
│  Pending_Approval/ → Human Review → Approved/ → Execute     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Personal_AI_Employee/
├── orchestrator.py              # Main coordination brain
├── watchers/                    # Perception layer
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   ├── filesystem_watcher.py
│   └── whatsapp_*.py            # WhatsApp helpers
├── mcp/                         # Action layer (7 servers)
│   ├── email/server.py
│   ├── filesystem/server.py
│   ├── approval/server.py
│   ├── linkedin/server.py
│   ├── twitter/server.py
│   ├── social/server.py         # Facebook + Instagram
│   └── odoo/server.py
├── scripts/                     # Operations
│   ├── cron/                    # Scheduled tasks
│   ├── start_odoo.sh            # Start Odoo Docker
│   ├── setup_cron.sh            # Install cron jobs
│   └── test_odoo.py             # Odoo tests
├── demo/                        # Demo & validation
│   ├── validate_gold_tier.py
│   ├── end_to_end_demo.py
│   └── demo_script.sh           # Video recording guide
├── docs/                        # Documentation
│   ├── GOLD_TIER_CHECKLIST.md
│   ├── SOCIAL_MEDIA_SETUP.md
│   └── VIDEO_RECORDING_GUIDE.md
├── docker/odoo/                 # Odoo Docker setup
│   ├── docker-compose.yml
│   └── README.md
├── tests/                       # 17 test files
├── vault/                       # Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Approved/
│   ├── Done/
│   ├── Pending_Approval/
│   ├── Logs/
│   └── Briefings/
└── .claude/, .qwen/             # Agent skills
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# AI Providers (at least one required)
ANTHROPIC_API_KEY=sk-...
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...

# Email (Gmail OAuth)
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...

# Odoo Accounting
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key_here

# LinkedIn
LINKEDIN_ACCESS_TOKEN=...

# Twitter/X
TWITTER_BEARER_TOKEN=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...

# Facebook/Instagram
META_ACCESS_TOKEN=...
META_APP_ID=...
META_APP_SECRET=...
INSTAGRAM_ACCOUNT_ID=...

# System
DRY_RUN=true                    # Set false for production
VAULT_PATH=./vault
HEALTH_PORT=8080
```

**Security:** `.env` is in `.gitignore` - never commit credentials!

---

## 🎯 Usage Examples

### Process Needs_Action (Manual)

```bash
python orchestrator.py --vault ./vault
```

### Generate CEO Briefing

```bash
python scripts/generate_ceo_briefing.py --vault ./vault
cat vault/Briefings/$(date +%Y-%m-%d)_Monday_Briefing.md
```

### Test Odoo Integration

```bash
# Start Odoo
./scripts/start_odoo.sh

# Run tests
python scripts/test_odoo.py
```

### Setup Cron Jobs

```bash
# Preview
./scripts/setup_cron.sh --dry-run

# Install
./scripts/setup_cron.sh

# View
crontab -l
```

### Health Check

```bash
curl http://127.0.0.1:8080/health
./scripts/health_check.sh
```

---

## 🧪 Testing

### Run All Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

### Validate Gold Tier

```bash
python demo/validate_gold_tier.py --vault ./vault
```

### Integration Tests

```bash
python demo/simple_integration_test.py
python demo/test_all_mcp_servers.py
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & architecture |
| [AGENTS.md](AGENTS.md) | Technical specification |
| [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Operations guide |
| [GOLD_TIER_README.md](GOLD_TIER_README.md) | Gold Tier features |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Progress tracker |
| [docs/GOLD_TIER_CHECKLIST.md](docs/GOLD_TIER_CHECKLIST.md) | Completion checklist |
| [docs/SOCIAL_MEDIA_SETUP.md](docs/SOCIAL_MEDIA_SETUP.md) | Social API setup |
| [docs/VIDEO_RECORDING_GUIDE.md](docs/VIDEO_RECORDING_GUIDE.md) | Demo video guide |
| [docker/odoo/README.md](docker/odoo/README.md) | Odoo Docker setup |

---

## 🛠️ Troubleshooting

### Common Issues

**Q: Orchestrator won't start**
```bash
# Check Python version
python --version  # Need 3.10+

# Activate virtual environment
source .venv/bin/activate

# Check dependencies
pip install -r requirements.txt
```

**Q: WhatsApp Watcher fails**
```bash
# Test mode
python watchers/whatsapp_watcher.py --vault ./vault --test

# Check Playwright installed
playwright install chromium
```

**Q: Odoo connection fails**
```bash
# Check Odoo is running
curl http://localhost:8069

# Check Docker
docker-compose -f docker/odoo/docker-compose.yml ps

# Verify .env credentials
cat .env | grep ODOO
```

**Q: MCP servers not connecting**
```bash
# Test individual MCP server
python mcp/email/server.py

# Check .mcp.json configuration
cat .mcp.json
```

See: [Troubleshooting FAQ](requirements.md#troubleshooting-faq)

---

## 🚀 Deployment

### Local Development

```bash
# Start all services
./scripts/start_all.sh

# Check status
./scripts/status_all.sh

# View logs
./scripts/logs_all.sh
```

### Production (PM2)

```bash
# Install PM2
npm install -g pm2

# Start services
pm2 start ecosystem.config.js

# Save process list
pm2 save

# Startup on boot
pm2 startup
```

### Cloud VM (Platinum Tier)

See: [Platinum Tier Requirements](requirements.md#platinum-tier-always-on-cloud--local-executor)

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Validation Score | 88% (45/51) |
| Test Files | 17 |
| MCP Servers | 7 |
| Total MCP Tools | 49 |
| Watchers | 3 |
| Agent Skills | 50 |
| Cron Jobs | 4 |
| Lines of Code | ~15,000+ |

---

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

---

## 📜 License

MIT License - See LICENSE file

---

## 🏆 Hackathon Submission

**Tier:** Gold Tier  
**Status:** In Progress (85%)  
**Validation:** 88%  
**Team:** Muhammad Tayyab  

**Submission Checklist:**
- [x] GitHub repository
- [x] README with setup instructions
- [x] Architecture documentation
- [ ] Demo video (5-10 min)
- [x] Security disclosure
- [ ] Submission form

**Form:** https://forms.gle/JR9T1SJq5rmQyGkGA

---

## 📞 Support

- **Research Meetings:** Wednesdays 10:00 PM Zoom
- **YouTube:** https://www.youtube.com/@panaversity
- **Documentation:** See `docs/` folder
- **Issues:** GitHub Issues

---

## 🙏 Acknowledgments

- Panaversity Hackathon
- Claude Code (Anthropic)
- Obsidian
- Model Context Protocol
- Odoo Community Edition

---

**Built with ❤️ for the Panaversity Personal AI Employee Hackathon 2026**

*Last Updated: 2026-04-13*
