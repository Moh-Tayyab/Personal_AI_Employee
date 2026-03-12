# 🚀 FREE AI Employee Setup Guide (4GB RAM)

## Complete Setup for Low-RAM Systems

### ✅ What's Already Working

| Component | Status | Notes |
|-----------|--------|-------|
| Gmail OAuth | ✅ Complete | Connected & tested |
| Email Sending | ✅ Working | Real emails sent |
| PM2 Process Mgmt | ✅ Running | Auto-restart enabled |
| Gmail Watcher | ✅ Active | Checking every 2 min |
| Ollama | ✅ Installed | v0.17.7 |

### ⏳ What's Downloading

| Component | Status | Time Remaining |
|-----------|--------|----------------|
| LLM Model | ⏳ Downloading | ~40 minutes |

---

## 📋 Step-by-Step Setup

### Step 1: Wait for Model Download

The LLM model is downloading in background. Check progress:

```bash
tail -f /tmp/ollama_pull.log
```

Wait until you see "success" message.

### Step 2: Start Ollama Service

```bash
# Start Ollama server
ollama serve &

# Verify it's running
ollama list
```

You should see:
```
NAME              ID           SIZE
qwen2.5:0.5b      xxxxx        ~400 MB
```

### Step 3: Test Ollama

```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
source .venv/bin/activate
python3 scripts/ollama_integration.py
```

Expected output:
```
✅ Ollama is running
📝 Testing with simple query...
Response: Hello! I am...
✅ Ollama integration test complete!
```

### Step 4: Restart Orchestrator

```bash
pm2 restart orchestrator
pm2 logs orchestrator --lines 20
```

You should see:
```
Triggering Ollama LLM with prompt...
Ollama executed successfully
```

### Step 5: Test Auto-Reply

Send a test email to `m.tayyab1263@gmail.com`:
```
Subject: Test Auto Reply
Body: Hello, testing the auto-reply system.
```

Within 2 minutes, you should get an AI-generated reply!

---

## 🔧 Troubleshooting

### Problem: Ollama not running

```bash
# Start Ollama
ollama serve &

# Or use PM2 for auto-start
pm2 start ollama --name "ollama-server" -- "ollama" "serve"
```

### Problem: Model not found

```bash
# Pull the model manually
ollama pull qwen2.5:0.5b

# This is a small model (~400MB), should download in 5-10 minutes
```

### Problem: Orchestrator errors

```bash
# Check logs
pm2 logs orchestrator --lines 50

# Restart if needed
pm2 restart orchestrator
```

### Problem: Out of memory

If you get "Out of memory" errors:

```bash
# Use even smaller model
ollama pull qwen2.5:0.5b

# Or set memory limit
OLLAMA_MAX_VRAM=2000 ollama serve
```

---

## 📊 Current System Status

```bash
# Check all services
pm2 status

# Expected output:
# ┌────┬─────────────┬──────────┬─────────┐
# │ id │ name        │ status   │ uptime  │
# ├────┼─────────────┼──────────┼─────────┤
# │ 0  │ gmail-watcher│ online   │ X min   │
# │ 1  │ orchestrator │ online   │ X min   │
# └────┴─────────────┴──────────┴─────────┘
```

---

## 🎯 Final Configuration

### Ollama Settings (for 4GB RAM)

```bash
# Create Ollama config
mkdir -p ~/.ollama
cat > ~/.ollama/config.json << 'EOF'
{
  "maxMemory": 2048,
  "maxVRAM": 1024
}
EOF
```

### PM2 Auto-Start

```bash
# Save current process list
pm2 save

# Setup PM2 startup (requires sudo)
pm2 startup

# This ensures services start on boot
```

---

## ✅ Completion Checklist

- [ ] Model download complete
- [ ] Ollama server running
- [ ] Test query successful
- [ ] Orchestrator restarted
- [ ] Test email sent
- [ ] Auto-reply received

---

## 🎉 What You Get

Once complete:

✅ **Email Auto-Reply** - AI reads & responds to emails
✅ **Smart Categorization** - Urgent/High/Normal/Low priority
✅ **24/7 Monitoring** - Gmail checked every 2 minutes
✅ **Free & Local** - No API costs, runs on your machine
✅ **Low RAM** - Optimized for 4GB systems

---

## 📞 Quick Commands

```bash
# Check status
pm2 status

# View logs
pm2 logs

# Restart all
pm2 restart all

# Monitor resources
pm2 monit

# Check Ollama
ollama list
```

---

**Setup in progress! Model download will complete in ~40 minutes.** ⏳
