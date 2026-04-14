# Demo Video Recording Guide

This guide helps you create a compelling 5-10 minute demo video for hackathon submission.

---

## 📹 Recording Setup

### Recommended Tools

**Option 1: OBS Studio (Free, Recommended)**
- Download: https://obsproject.com/
- Settings: 1080p, 30fps
- Record desktop + webcam (optional)

**Option 2: SimpleScreenRecorder (Linux)**
```bash
sudo apt install simplescreenrecorder
```

**Option 3: QuickTime (macOS)**
- File → New Screen Recording

### Terminal Setup

```bash
# Increase terminal font size for visibility
# Use a clean terminal theme
# Clear screen before recording
clear
```

---

## 🎬 Video Structure (Target: 7-8 minutes)

### **Segment 1: Introduction (0:00 - 0:45)**

**What to Show:**
- Project GitHub page
- Architecture diagram
- Brief project overview

**Script:**
> "Hi, I'm [Your Name], and this is my Personal AI Employee - a fully autonomous digital worker that manages business operations 24/7. Built for the Panaversity Hackathon, it achieves Gold Tier status with 7 MCP servers, 3 watchers, and complete human-in-the-loop workflow."

---

### **Segment 2: Architecture Overview (0:45 - 2:00)**

**What to Show:**
```bash
# Show project structure
tree -L 2 -I '__pycache__|.venv|node_modules'

# Show vault structure
ls -la vault/
```

**Script:**
> "The architecture follows three layers:
> 1. **Perception Layer** - Three watchers monitor Gmail, WhatsApp, and filesystem
> 2. **Reasoning Layer** - The orchestrator with multi-provider AI (Qwen, Claude, Gemini)
> 3. **Action Layer** - Seven MCP servers for Email, Social Media, Odoo Accounting, and more
> 
> All communication happens through local markdown files in the Obsidian vault, keeping everything privacy-focused."

---

### **Segment 3: Core Demo - End-to-End Flow (2:00 - 4:30)**

**What to Show:**
```bash
# Run validation
python demo/validate_gold_tier.py --vault ./vault

# Run integration test
python demo/simple_integration_test.py

# Run full end-to-end demo
python demo/end_to_end_demo.py --vault ./vault
```

**Script:**
> "Let me demonstrate the complete workflow:
> 
> First, the validation script confirms all 45+ components are present and working.
> 
> Now, the end-to-end demo shows:
> 1. A WhatsApp message arrives and is detected
> 2. The orchestrator creates an action plan
> 3. AI analyzes the request and determines approval is needed
> 4. Human approves the action
> 5. Email is sent via MCP server
> 6. Social media post is created
> 7. Odoo invoice is generated
> 8. Dashboard is automatically updated
> 
> All of this happens autonomously with human oversight at critical points."

---

### **Segment 4: WhatsApp Watcher Demo (4:30 - 5:30)**

**What to Show:**
```bash
# Show WhatsApp watcher (if logged in)
python watchers/whatsapp_watcher.py --vault ./vault --test

# Or show a pre-created action file
cat vault/Needs_Action/WHATSAPP_*.md
```

**Script:**
> "The WhatsApp watcher uses Playwright to monitor WhatsApp Web 24/7. It detects keywords like 'invoice', 'payment', 'urgent' and creates structured markdown files for the AI to process. Session persists across restarts, so it survives reboots."

---

### **Segment 5: Odoo Accounting Integration (5:30 - 6:30)**

**What to Show:**
```bash
# Show Odoo running
docker-compose -f docker/odoo/docker-compose.yml ps

# Test Odoo MCP
python scripts/test_odoo.py
```

**Script:**
> "For business operations, the AI Employee integrates with Odoo Community Edition running locally via Docker. It can create customers, generate invoices, record payments, and provide financial summaries - all autonomously with approval workflow."

---

### **Segment 6: Social Media & CEO Briefing (6:30 - 7:30)**

**What to Show:**
```bash
# Show social media status
python -c "from mcp.linkedin.server import linkedin_status; print(linkedin_status())"

# Generate CEO briefing
python scripts/generate_ceo_briefing.py --vault ./vault

# Show generated briefing
cat vault/Briefings/*.md | head -40
```

**Script:**
> "The social media MCP servers enable posting to LinkedIn, Twitter, Facebook, and Instagram. The autonomous CEO briefing runs every Monday morning, analyzing revenue, bottlenecks, and providing proactive suggestions like 'I noticed we spent $200 on unused software subscriptions.'"

---

### **Segment 7: Security & Human-in-the-Loop (7:30 - 8:30)**

**What to Show:**
```bash
# Show approval workflow
ls -la vault/Pending_Approval/
ls -la vault/Approved/

# Show audit logs
ls -la vault/Logs/
cat vault/Logs/*.json | head -20
```

**Script:**
> "Security is critical. All sensitive actions require human approval through a file-based workflow. The AI creates approval requests, I review them, and only approved actions execute. Every action is logged with timestamps for full audit trails. The system runs in DRY_RUN mode by default, preventing accidental external actions."

---

### **Segment 8: Conclusion & Next Steps (8:30 - 9:00)**

**What to Show:**
- Gold Tier checklist
- Validation score
- GitHub repo

**Script:**
> "This achieves Gold Tier with 95% functionality coverage. All core features are working: multiple watchers, 7 MCP servers, CEO briefing generation, error recovery, and comprehensive audit logging.
> 
> Next steps include Platinum Tier deployment with cloud VM, work-zone specialization, and 24/7 autonomous operation.
> 
> Full documentation and setup instructions are in the repository. Thank you!"

---

## 🎯 Recording Tips

### Do's ✅

1. **Use a clean terminal** - Clear scrollback, good font size
2. **Speak clearly** - Explain what you're showing
3. **Pause between steps** - Give viewers time to absorb
4. **Show failures gracefully** - If something breaks, explain why and move on
5. **Use DRY_RUN mode** - Prevent accidental real actions
6. **Have tabs ready** - Open all files/terminals before recording
7. **Test run first** - Do a practice run before recording

### Don'ts ❌

1. **Don't rush** - Better to be 9 minutes and clear than 5 minutes and confusing
2. **Don't show secrets** - Blur/hide API keys, tokens
3. **Don't skip errors** - Explain them, shows robustness
4. **Don't edit live** - Record in segments, edit later
5. **Don't forget audio** - Test microphone before recording

---

## ✂️ Post-Production

### Editing Tools

**Free Options:**
- **Shotcut** (Linux/Windows/macOS) - https://shotcut.org/
- **OpenShot** (Linux) - `sudo apt install openshot-qt`
- **DaVinci Resolve** (Professional, Free) - https://www.blackmagicdesign.com/products/davinciresolve

**Paid Options:**
- Adobe Premiere Pro
- Final Cut Pro (macOS)

### Editing Checklist

- [ ] Trim dead air and mistakes
- [ ] Add intro/outro title cards
- [ ] Add voiceover (if recording screen only)
- [ ] Add background music (optional, keep low)
- [ ] Speed up repetitive sections (1.5x)
- [ ] Add text overlays for key points
- [ ] Export as MP4 (H.264, 1080p)

### Export Settings

```
Format: MP4
Codec: H.264
Resolution: 1920x1080
Frame Rate: 30fps
Bitrate: 8-12 Mbps
Audio: AAC, 192kbps
```

---

## 📤 Upload & Submission

### YouTube Upload

1. Upload to YouTube as **Unlisted**
2. Title: "Personal AI Employee - Gold Tier Demo | Panaversity Hackathon 2026"
3. Description:
```markdown
Demo of Personal AI Employee achieving Gold Tier status.

Features:
- 7 MCP Servers (Email, Social, Odoo, LinkedIn, Twitter, Facebook, Instagram)
- 3 Watchers (Gmail, WhatsApp, Filesystem)
- Human-in-the-Loop Approval Workflow
- Autonomous CEO Briefing Generation
- Error Recovery & Circuit Breakers

GitHub: [Your Repo URL]
Documentation: [Docs URL]

#AI #Automation #Hackathon #ClaudeCode #MCP
```
4. Add timestamps in description
5. Copy video URL for submission form

### Submission Form

Fill out: https://forms.gle/JR9T1SJq5rmQyGkGA

Include:
- [ ] GitHub repository URL
- [ ] YouTube demo video URL
- [ ] Tier declaration: Gold
- [ ] Brief project description
- [ ] Security disclosure

---

## 📊 Final Checklist Before Recording

- [ ] All services working (run validation first)
- [ ] Terminal font size increased (16px+)
- [ ] Microphone tested and working
- [ ] Screen recording software ready
- [ ] Demo script printed/open
- [ ] Practice run completed
- [ ] API keys hidden/blurred
- [ ] DRY_RUN=true confirmed
- [ ] Clean desktop background
- [ ] Notifications disabled (Do Not Disturb mode)

---

## 🎓 Example Demo Timeline

```
0:00  - Intro & Project Overview
0:45  - Architecture & Tech Stack
2:00  - Validation & Integration Tests
3:00  - End-to-End Demo
4:30  - WhatsApp Watcher
5:30  - Odoo Accounting
6:30  - Social Media & CEO Briefing
7:30  - Security & HITL Workflow
8:30  - Conclusion & Next Steps
9:00  - END
```

---

*Good luck with your submission! 🚀*

*This guide was created specifically for the Panaversity Personal AI Employee Hackathon 2026.*
