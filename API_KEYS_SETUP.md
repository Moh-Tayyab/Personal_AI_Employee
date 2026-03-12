# Multi-Provider AI System - API Keys Setup Guide

## 🔑 API Keys Setup (Required for Full Functionality)

### Step 1: Set Environment Variables

```bash
# Add to your .env file or export directly:

# Anthropic (Primary - supports thinking mode)
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# OpenRouter (Secondary - cost effective)
export OPENROUTER_API_KEY="your_openrouter_key_here"

# Gemini (Tertiary - very cheap/free)
export GEMINI_API_KEY="your_gemini_key_here"
```

### Step 2: Get API Keys

#### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Create account / Login
3. Go to API Keys section
4. Create new key
5. Copy and set as ANTHROPIC_API_KEY

#### OpenRouter API Key
1. Go to https://openrouter.ai/
2. Sign up / Login
3. Go to Keys section
4. Create new key
5. Copy and set as OPENROUTER_API_KEY

#### Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Create Google account / Login
3. Create API key
4. Copy and set as GEMINI_API_KEY

### Step 3: Test with API Keys

```bash
# Test the system
python3 scripts/test_multi_provider_integration.py

# Should now show:
# Provider Used: anthropic (or openrouter/gemini)
# Tools Integration: ✅ WORKING
# MCP Integration: ✅ WORKING
# Skills Integration: ✅ WORKING
```

## 🚀 Real-World Usage Examples

### Example 1: Email Processing with Full Claude Code Features
```bash
# This will work exactly like Claude Code:
python3 orchestrator.py --vault ./vault --live

# When email arrives:
# 1. Uses thinking mode (if Anthropic available)
# 2. Uses all tools (bash, read, write, etc.)
# 3. Uses MCP servers (email server to send replies)
# 4. Uses skills (/process-emails)
# 5. Falls back to cheaper provider if quota exhausted
```

### Example 2: Playwright Automation
```bash
# Browser automation with fallback:
# 1. Primary: Anthropic with full thinking + tools + Playwright MCP
# 2. Fallback: OpenRouter with tools + Playwright MCP
# 3. Final: Gemini with basic tools + Playwright MCP
```

### Example 3: Agent Teams Coordination
```bash
# Multiple specialized agents:
# 1. Research Agent (uses web_search tool + thinking mode)
# 2. Planning Agent (uses thinking mode + file tools)
# 3. Execution Agent (uses MCP servers + bash tools)
# 4. All coordinated through multi-provider system
```

## 💡 Key Benefits Over Original Claude Code

### 1. Never Gets Stuck
```
❌ Before: "Claude quota exceeded, wait 24 hours"
✅ Now: "Claude quota exceeded, switching to OpenRouter... task completed!"
```

### 2. Cost Optimization
```
💰 Simple tasks → Gemini (very cheap)
🧠 Complex reasoning → Anthropic (thinking mode)
⚖️ Balanced tasks → OpenRouter (middle cost)
```

### 3. Performance Optimization
```
🎯 Code tasks → Best available provider
🧠 Reasoning tasks → Anthropic (thinking mode)
🛠️ Tool tasks → Any provider with tool support
```

## 🔧 Configuration Examples

### Prefer Cost Savings
```yaml
# vault/config/ai_providers.yaml
routing:
  simple: [gemini, openrouter, anthropic]
  general: [gemini, openrouter, anthropic]
  reasoning: [anthropic]  # Only for complex thinking
```

### Prefer Performance
```yaml
routing:
  simple: [anthropic, openrouter, gemini]
  general: [anthropic, openrouter, gemini]
  reasoning: [anthropic]
```

### Prefer Reliability
```yaml
routing:
  simple: [openrouter, anthropic, gemini]
  general: [openrouter, anthropic, gemini]
  reasoning: [anthropic, openrouter]
```