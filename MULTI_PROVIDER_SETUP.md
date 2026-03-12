# Multi-Provider AI Support - Personal AI Employee

The system now supports **3 AI providers** (tries in order):

## Supported Providers

### 1. Google Gemini (Recommended - Free Tier Available)
- **Model:** Gemini 1.5 Pro
- **Free tier:** 15 requests/minute, 1 million tokens/day
- **Cost:** Free for most use cases
- **Get API key:** https://makersuite.google.com/app/apikey

**Add to .env:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. OpenRouter (Flexible)
- **Model:** Claude 3.5 Sonnet (via OpenRouter)
- **Cost:** Pay per use (~$0.01/email)
- **Get API key:** https://openrouter.ai/keys

**Add to .env:**
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

### 3. Anthropic Direct (Most Reliable)
- **Model:** Claude Sonnet 4.6
- **Free tier:** $5 credits for new accounts
- **Cost:** $3 input / $15 output per million tokens
- **Get API key:** https://console.anthropic.com

**Add to .env:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## How It Works

The system tries providers in this order:
1. **Gemini** (if GEMINI_API_KEY is set)
2. **OpenRouter** (if OPENROUTER_API_KEY is set)
3. **Anthropic** (if ANTHROPIC_API_KEY is set)
4. **Rule-based fallback** (if no API keys work)

If one fails, it automatically tries the next one.

---

## Quick Setup - Get Gemini API Key (FREE)

### Step 1: Get API Key (2 minutes)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Select or create a Google Cloud project
4. Copy the API key

### Step 2: Add to .env (30 seconds)
```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### Step 3: Test (1 minute)
```bash
source .venv/bin/activate
python test_setup.py
```

---

## Test Each Provider

### Test Gemini
```bash
python -c "
from orchestrator import Orchestrator
from dotenv import load_dotenv
import os

load_dotenv()
os.environ['OPENROUTER_API_KEY'] = ''  # Disable OpenRouter
os.environ['ANTHROPIC_API_KEY'] = ''   # Disable Anthropic

orch = Orchestrator('./vault', dry_run=False)
result = orch.trigger_claude('Test email: Hello')
print('✅ Gemini works!' if result else '❌ Failed')
"
```

### Test OpenRouter
```bash
python -c "
from orchestrator import Orchestrator
from dotenv import load_dotenv
import os

load_dotenv()
os.environ['GEMINI_API_KEY'] = ''      # Disable Gemini
os.environ['ANTHROPIC_API_KEY'] = ''   # Disable Anthropic

orch = Orchestrator('./vault', dry_run=False)
result = orch.trigger_claude('Test email: Hello')
print('✅ OpenRouter works!' if result else '❌ Failed')
"
```

### Test Anthropic
```bash
python -c "
from orchestrator import Orchestrator
from dotenv import load_dotenv
import os

load_dotenv()
os.environ['GEMINI_API_KEY'] = ''      # Disable Gemini
os.environ['OPENROUTER_API_KEY'] = ''  # Disable OpenRouter

orch = Orchestrator('./vault', dry_run=False)
result = orch.trigger_claude('Test email: Hello')
print('✅ Anthropic works!' if result else '❌ Failed')
"
```

---

## Pricing Comparison

| Provider | Free Tier | Cost per Email | Best For |
|----------|-----------|----------------|----------|
| **Gemini** | 1M tokens/day | FREE | Personal use, testing |
| **OpenRouter** | No free tier | ~$0.01 | Flexibility, multiple models |
| **Anthropic** | $5 credits | ~$0.01 | Production, reliability |

**Recommendation:** Start with Gemini (free), upgrade to Anthropic for production.

---

## Current Status

Your .env file currently has:
- ✅ OPENROUTER_API_KEY (but returned 401 error - might be invalid)
- ❌ GEMINI_API_KEY (not set)
- ❌ ANTHROPIC_API_KEY (not set)

**Next step:** Add GEMINI_API_KEY to get AI working for free!

---

## Updated .env.example

```bash
# AI Provider API Keys (system tries in order: Gemini → OpenRouter → Anthropic)

# Google Gemini (FREE - Recommended for personal use)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenRouter (Pay per use - Flexible)
OPENROUTER_API_KEY=your_openrouter_key_here

# Anthropic Direct (Pay per use - Most reliable)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Gmail API
GMAIL_CREDENTIALS_PATH=./vault/secrets/gmail_credentials.json
GMAIL_TOKEN_PATH=./vault/secrets/gmail_token.json

# System Configuration
VAULT_PATH=./vault
DRY_RUN=false
LOG_LEVEL=INFO
```
