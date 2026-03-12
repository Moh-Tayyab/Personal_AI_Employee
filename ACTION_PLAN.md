# 🎯 Action Plan - Get Your AI Employee Running

**Current Status:** 95% Complete | Just Need API Key
**Time to Complete:** 5-10 minutes

---

## ✅ Step-by-Step Checklist

### □ Step 1: Get Anthropic API Key (5 min)

1. **Open browser:** https://console.anthropic.com
2. **Sign up or log in** with your email
3. **Navigate to:** Settings → API Keys
4. **Click:** "Create Key"
5. **Copy the key** (starts with `sk-ant-`)
6. **Save it** - you'll need it in the next step

**Note:** New accounts get $5 free credits (~500 emails)

---

### □ Step 2: Add API Key to .env (1 min)

```bash
# Option 1: Add via command line
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env

# Option 2: Edit .env file manually
nano .env
# Add this line at the end:
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Verify it was added:**
```bash
grep ANTHROPIC_API_KEY .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

---

### □ Step 3: Run Tests (1 min)

```bash
source .venv/bin/activate
python test_setup.py
```

**Expected output:**
```
✅ ANTHROPIC_API_KEY set
✅ Claude API connection
   Response: OK

Test Summary
Total tests: 7
Passed: 7  ← Should be 7/7 now
Failed: 0

✅ All tests passed! System is ready to use.
```

---

### □ Step 4: Run Interactive Demo (5 min)

```bash
python demo.py
```

**What you'll see:**
1. Claude API integration demo
2. Email operations demo
3. Approval workflow demo
4. End-to-end workflow demo

**Press Enter** to advance through each demo.

---

### □ Step 5: Process Your First Email (2 min)

**Option A: Create test email**
```bash
cat > vault/Needs_Action/test_email.md << 'EOF'
---
type: email
from: test@example.com
subject: Test: Can you help with project planning?
date: 2026-03-10
---

Hi Muhammad,

I need help planning the Q2 project timeline. Can we discuss this week?

Thanks,
Test User
EOF
```

**Option B: Use real email**
```bash
# Start Gmail watcher to fetch real emails
python watchers/gmail_watcher.py --vault ./vault
```

---

### □ Step 6: Process with Claude (1 min)

```bash
# Process the test email
python orchestrator.py --vault ./vault --dry-run

# Check the results
ls -la vault/Plans/CLAUDE_PLAN_*.md
cat vault/Plans/CLAUDE_PLAN_*.md
```

**Expected output:**
```
2026-03-10 22:50:00 - INFO - Processing with Claude AI
2026-03-10 22:50:02 - INFO - Claude response received
2026-03-10 22:50:02 - INFO - Claude plan saved

✅ Claude processed the email successfully!
```

---

### □ Step 7: Review Claude's Plan

```bash
# View the latest plan
cat vault/Plans/CLAUDE_PLAN_*.md | tail -50
```

**You should see:**
- Analysis of the email
- Recommended actions
- Priority level
- Whether approval is needed
- Category classification

---

### □ Step 8: Start the System (Optional)

**For testing:**
```bash
# Run in foreground (Ctrl+C to stop)
python orchestrator.py --vault ./vault
```

**For production:**
```bash
# Run with PM2 (background)
pm2 start ecosystem.config.js
pm2 status
pm2 logs
```

---

## 🎯 Quick Verification Commands

After adding API key, run these to verify everything works:

```bash
# 1. Test Claude API directly
python -c "
from anthropic import Anthropic
from dotenv import load_dotenv
import os
load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
msg = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Say OK if you can read this'}]
)
print('✅ Claude API works:', msg.content[0].text)
"

# 2. Test orchestrator with Claude
python -c "
from orchestrator import Orchestrator
from dotenv import load_dotenv
load_dotenv()
orch = Orchestrator('./vault', dry_run=False)
result = orch.trigger_claude('Test email: Hello world')
print('✅ Orchestrator works!' if result else '❌ Failed')
"

# 3. Check what was created
ls -la vault/Plans/CLAUDE_PLAN_*.md
ls -la vault/Drafts/
```

---

## 📁 What I Created for You

### Documentation (Read in This Order)
1. **WHATS_WORKING_NOW.md** ← Start here (what works right now)
2. **TEST_RESULTS.md** ← Test results and status
3. **QUICKSTART.md** ← 5-minute quick start
4. **SETUP.md** ← Complete setup guide
5. **SESSION_COMPLETE.md** ← Full session summary

### Deep Dive
6. **TIER_AUDIT.md** ← What's actually implemented (Q/A format)
7. **IMPLEMENTATION_STATUS.md** ← What was fixed today
8. **SUMMARY.md** ← Executive summary

### Tools
9. **test_setup.py** ← Run this to verify setup
10. **demo.py** ← Interactive demo of all features
11. **tests/test_integration.py** ← Integration tests

### Configuration
12. **requirements.txt** ← All dependencies (installed)
13. **.env.example** ← Configuration template
14. **vault/secrets/webhooks.json.example** ← Webhook config

---

## 🚨 Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
```bash
# Check if .env exists
ls -la .env

# Check if key is in .env
grep ANTHROPIC_API_KEY .env

# If missing, add it
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

### Issue: "API key invalid"
```bash
# Test the key directly
python -c "
from anthropic import Anthropic
client = Anthropic(api_key='sk-ant-your-key-here')
try:
    msg = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=10,
        messages=[{'role': 'user', 'content': 'Hi'}]
    )
    print('✅ Key works!')
except Exception as e:
    print('❌ Key invalid:', e)
"
```

### Issue: Tests still failing
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Run tests with verbose output
python test_setup.py 2>&1 | tee test_output.log
```

---

## 📊 Progress Tracker

**Before This Session:**
- [ ] Claude integration
- [ ] Email sending
- [ ] Email search
- [ ] Dependencies documented
- [ ] Setup guide

**After This Session:**
- [x] Claude integration (code ready)
- [x] Email sending (working)
- [x] Email search (working)
- [x] Dependencies documented
- [x] Setup guide created
- [x] Tests created
- [x] Demo created
- [ ] API key added ← **YOU ARE HERE**

**After Adding API Key:**
- [x] All 7/7 tests passing
- [x] Claude AI working
- [x] Full AI employee functionality
- [x] Ready for production

---

## 🎉 Success Criteria

You'll know it's working when:

1. **Test passes:** `python test_setup.py` shows 7/7 ✅
2. **Claude responds:** Demo shows Claude analyzing emails
3. **Plans created:** Files appear in `vault/Plans/CLAUDE_PLAN_*.md`
4. **Intelligent analysis:** Plans show context understanding, not just keywords

---

## 📞 Need Help?

**If stuck:**
1. Check TEST_RESULTS.md for current status
2. Run `python test_setup.py` to see what's failing
3. Check logs in `vault/Logs/`
4. Review SETUP.md for detailed instructions

**Common issues:**
- API key not set → Add to .env
- Dependencies missing → Run `pip install -r requirements.txt`
- Gmail not authenticated → Run `python watchers/gmail_watcher.py`

---

## ⏭️ After It's Working

### Customize Your AI Employee
1. Edit `vault/Company_Handbook.md` - Add your rules
2. Edit `vault/Business_Goals.md` - Set your goals
3. Add webhook URLs to .env - Get notifications

### Start Using It
1. Let Gmail watcher run continuously
2. Orchestrator processes emails automatically
3. Review plans in `vault/Plans/`
4. Approve items in `vault/Pending_Approval/`

### Monitor Performance
1. Check `vault/Logs/` daily
2. Review `vault/Dashboard.md`
3. Generate CEO briefing: `python scripts/generate_briefing.py`

---

## 🎯 Your Next Command

**Right now, run this:**

```bash
# If you have the API key, add it:
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env

# Then test:
python test_setup.py

# If 7/7 pass, run demo:
python demo.py
```

**If you don't have the API key yet:**
1. Go to https://console.anthropic.com
2. Create account
3. Get API key
4. Come back and run the commands above

---

**You're one command away from a fully functional AI employee! 🚀**
