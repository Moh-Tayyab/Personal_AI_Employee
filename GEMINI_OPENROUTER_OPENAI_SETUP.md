# API Keys Setup Guide - Gemini + OpenRouter + OpenAI Configuration

## 🔑 **Your Optimal Setup (Cost-Effective & Powerful)**

### **Provider Priority:**
1. **🥇 Gemini** - Primary (Very cheap/free, excellent performance)
2. **🥈 OpenRouter** - Secondary (Access to Claude 3.5 Sonnet)
3. **🥉 OpenAI** - Tertiary (GPT-4o for code tasks)

## 🚀 **Step-by-Step API Key Setup**

### **1. Gemini API Key (FREE/Very Cheap - Primary)**

```bash
# Get Gemini API Key:
# 1. Go to https://makersuite.google.com/app/apikey
# 2. Sign in with Google account
# 3. Click "Create API key"
# 4. Copy the key

# Set environment variable:
export GEMINI_API_KEY="your_gemini_api_key_here"

# Add to .env file:
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
```

**Benefits:**
- ✅ FREE tier with generous limits
- ✅ Very fast responses
- ✅ Excellent for most tasks
- ✅ Tool support included

### **2. OpenRouter API Key (Cost-Effective - Secondary)**

```bash
# Get OpenRouter API Key:
# 1. Go to https://openrouter.ai/
# 2. Sign up / Login
# 3. Go to "Keys" section
# 4. Create new key
# 5. Add some credits ($5-10 recommended)

# Set environment variable:
export OPENROUTER_API_KEY="your_openrouter_api_key_here"

# Add to .env file:
echo "OPENROUTER_API_KEY=your_openrouter_api_key_here" >> .env
```

**Benefits:**
- ✅ Access to Claude 3.5 Sonnet (best reasoning)
- ✅ 20% cheaper than direct Anthropic
- ✅ Multiple models available
- ✅ Pay-per-use pricing

### **3. OpenAI API Key (Code Specialist - Tertiary)**

```bash
# Get OpenAI API Key:
# 1. Go to https://platform.openai.com/api-keys
# 2. Sign up / Login
# 3. Click "Create new secret key"
# 4. Copy the key
# 5. Add credits to your account

# Set environment variable:
export OPENAI_API_KEY="your_openai_api_key_here"

# Add to .env file:
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
```

**Benefits:**
- ✅ GPT-4o excellent for code generation
- ✅ Great tool integration
- ✅ Reliable and fast
- ✅ Good for development tasks

## 💰 **Cost Comparison (Your Setup vs Others)**

### **Your Setup (Optimized):**
```
🥇 Gemini: $0.001/1K tokens (FREE tier available)
🥈 OpenRouter: $0.012/1K tokens (Claude 3.5 Sonnet)
🥉 OpenAI: $0.010/1K tokens (GPT-4o)

Daily cost for 100K tokens: ~$0.10-0.60
Monthly cost: ~$3-18
```

### **Typical Setup (Expensive):**
```
❌ Anthropic Direct: $0.015/1K tokens
❌ OpenAI Direct: $0.010/1K tokens
❌ No free tier

Daily cost for 100K tokens: $1.00-1.50
Monthly cost: $30-45
```

**Your Savings: 80-90%!** 🎉

## 🧪 **Quick Test Setup**

```bash
# 1. Set at least one API key (Gemini recommended for free tier)
export GEMINI_API_KEY="your_key_here"

# 2. Test the system
python3 scripts/check_api_keys.py

# 3. Test multi-provider system
python3 scripts/multi_provider_ai.py --status

# 4. Run a test
python3 scripts/multi_provider_ai.py --test
```

## 🎯 **Recommended Setup Order**

### **Minimum Setup (FREE):**
```bash
# Just Gemini (free tier)
export GEMINI_API_KEY="your_key"
```

### **Optimal Setup (Best Value):**
```bash
# Gemini + OpenRouter
export GEMINI_API_KEY="your_key"
export OPENROUTER_API_KEY="your_key"
```

### **Complete Setup (Maximum Capability):**
```bash
# All three providers
export GEMINI_API_KEY="your_key"
export OPENROUTER_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

## 🔧 **Configuration for Your Needs**

### **Cost-Optimized (Gemini First):**
```yaml
# vault/config/ai_providers.yaml already configured for this!
routing:
  simple: [gemini, openrouter, openai]
  general: [gemini, openrouter, openai]
  code: [openai, openrouter, gemini]  # OpenAI best for code
```

### **Performance-Optimized:**
```yaml
routing:
  simple: [gemini, openrouter, openai]
  reasoning: [openrouter, openai, gemini]  # Claude for reasoning
  code: [openai, gemini, openrouter]       # OpenAI for code
```

## 🚀 **Ready to Start**

```bash
# 1. Set your API keys
export GEMINI_API_KEY="your_key"
export OPENROUTER_API_KEY="your_key"  # Optional but recommended
export OPENAI_API_KEY="your_key"      # Optional for code tasks

# 2. Test everything works
python3 scripts/multi_provider_ai.py --status

# 3. Start your AI employee
python3 orchestrator.py --vault ./vault --live

# 4. Drop emails in vault/Needs_Action/ and watch it work!
```

## 💡 **Pro Tips**

1. **Start with Gemini only** (free tier) to test everything
2. **Add OpenRouter** when you need Claude's reasoning power
3. **Add OpenAI** when you do lots of code generation
4. **Monitor costs** with the built-in tracking system
5. **Adjust routing** based on your usage patterns

Your setup is now **enterprise-grade** with **maximum cost savings**! 🎉