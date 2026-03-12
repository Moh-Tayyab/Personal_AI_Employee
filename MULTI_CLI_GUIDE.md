# Multi-CLI System - Complete Usage Guide

## 🚀 Quick Start

### 1. **Basic Setup**
```bash
# Test all CLIs
python3 orchestrator.py --vault ./vault --test-clis

# Check quota status
python3 orchestrator.py --vault ./vault --quota-status

# Start with automatic fallback (recommended)
python3 orchestrator.py --vault ./vault --live --primary-cli claude
```

### 2. **Using Startup Scripts**
```bash
# Linux/macOS - Automatic fallback enabled
./scripts/start_multi_cli.sh --vault ./vault --live --primary-cli claude

# Windows - Automatic fallback enabled
scripts\start_multi_cli.bat --vault .\vault --live --primary-cli claude

# Force specific CLI (no fallback)
./scripts/start_multi_cli.sh --force-cli qwen --vault ./vault --live
```

## 📋 CLI Installation Guide

### **Claude CLI**
Already installed (you're using it now!)
- ✅ Available in current session
- ⚠️ Cannot run nested sessions (will auto-fallback to API)

### **Qwen CLI**
```bash
# Install Qwen CLI
pip install qwen-cli

# Test installation
qwen --help
```

### **GitHub Copilot CLI**
```bash
# Install GitHub CLI first (if not installed)
# Ubuntu/Debian:
sudo apt install gh

# Install Copilot extension
gh extension install github/gh-copilot

# Authenticate
gh auth login

# Test installation
gh copilot --version
```

## 🎯 Usage Scenarios

### **Scenario 1: Claude Quota Exhausted**
```bash
# System automatically detects and switches
2026-03-11 21:45:00 - INFO - 🔄 Trying claude...
2026-03-11 21:45:01 - WARNING - ❌ claude failed: Claude quota exhausted
2026-03-11 21:45:01 - INFO - 🔄 Trying qwen...
2026-03-11 21:45:02 - INFO - ✅ Success with qwen
```

### **Scenario 2: Force Specific CLI**
```bash
# Force Qwen for cost optimization
python3 orchestrator.py --vault ./vault --force-cli qwen --live

# Force Codex for code-heavy tasks
python3 orchestrator.py --vault ./vault --force-cli codex --live
```

### **Scenario 3: Windows Environment**
```batch
REM Test all CLIs on Windows
scripts\start_multi_cli.bat --test-only

REM Start with Qwen as primary (local, no API costs)
scripts\start_multi_cli.bat --vault .\vault --live --primary-cli qwen
```

## 🔧 Configuration

### **Edit CLI Preferences**
```yaml
# vault/config/cli_fallback.yaml
fallback_strategy:
  primary: "qwen"      # Change to qwen for cost savings
  secondary: "claude"  # Claude as backup
  tertiary: "codex"    # Codex for code tasks

quota_limits:
  claude:
    daily_limit: 500    # Reduce if on tight budget
    warning_threshold: 50
```

### **Task-Specific Routing**
```yaml
task_routing:
  code_generation: ["codex", "claude", "qwen"]     # Codex first for code
  reasoning: ["claude", "qwen", "codex"]           # Claude first for complex thinking
  simple_processing: ["qwen", "claude", "codex"]  # Qwen first for simple tasks
```

## 📊 Monitoring & Management

### **Check System Status**
```bash
# Comprehensive status
python3 scripts/multi_cli_manager.py --status

# Just quota info
python3 scripts/quota_manager.py --status

# Best CLI recommendation
python3 scripts/quota_manager.py --best-cli
```

### **Reset Quotas** (when they actually reset)
```bash
python3 scripts/quota_manager.py --reset
```

### **Test Individual CLIs**
```bash
# Test all CLIs
python3 scripts/multi_cli_manager.py --test

# Process a test prompt
python3 scripts/multi_cli_manager.py --process "Hello, how are you?"
```

## 🚨 Troubleshooting

### **Common Issues & Solutions**

#### **"No CLIs available"**
```bash
# Check what's installed
which claude qwen gh

# Install missing CLIs
pip install qwen-cli
gh extension install github/gh-copilot
```

#### **"Claude nested session error"**
✅ **Expected behavior** - System automatically falls back to API or other CLIs

#### **"Qwen command not found"**
```bash
# Install Qwen
pip install qwen-cli

# Or use local model
pip install qwen-local
```

#### **"Codex quota exceeded"**
```bash
# Check GitHub Copilot subscription
gh copilot --version

# System will auto-fallback to Claude/Qwen
```

### **Debug Mode**
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python3 orchestrator.py --vault ./vault --live
```

## 💡 Best Practices

### **1. Cost Optimization**
```bash
# Use Qwen as primary (local/free)
./scripts/start_multi_cli.sh --primary-cli qwen --vault ./vault --live

# Set conservative quotas
# Edit vault/config/cli_fallback.yaml:
# claude: daily_limit: 200
# codex: daily_limit: 100
```

### **2. Performance Optimization**
```bash
# For code-heavy workloads
./scripts/start_multi_cli.sh --primary-cli codex --vault ./vault --live

# For reasoning-heavy workloads
./scripts/start_multi_cli.sh --primary-cli claude --vault ./vault --live
```

### **3. Reliability Setup**
```bash
# Always have 2+ CLIs available
# Recommended setup:
# 1. Claude (primary) - best reasoning
# 2. Qwen (secondary) - local fallback
# 3. Codex (tertiary) - code specialist
```

## 📈 Advanced Usage

### **Programmatic Integration**
```python
from scripts.multi_cli_manager import MultiCLIManager

# Initialize
manager = MultiCLIManager("./vault")

# Process with best CLI
cli_used, result = manager.process_with_best_cli(
    prompt="Analyze this email and create action plan",
    context="Email from client about urgent project changes"
)

print(f"✅ Processed with {cli_used}")
print(f"📝 Result: {result}")
```

### **Custom Task Routing**
```python
# Override task type detection
def custom_task_type(content):
    if "invoice" in content.lower():
        return "finance"
    elif "code" in content.lower():
        return "code"
    else:
        return "general"

manager.determine_task_type = custom_task_type
```

### **Quota Monitoring**
```python
from scripts.quota_manager import QuotaManager

quota = QuotaManager("./vault")

# Check before processing
if quota.check_claude_quota():
    print("✅ Claude available")
else:
    print("⚠️ Claude quota exhausted")

# Get recommendations
best_cli = quota.get_best_available_cli()
print(f"🎯 Recommended: {best_cli}")
```

## 🔄 Integration with Personal AI Employee

The multi-CLI system is now fully integrated:

- **📧 Email Processing**: Routes through best available CLI
- **📋 Task Planning**: Uses Claude for complex reasoning, Qwen for simple tasks
- **💻 Code Tasks**: Automatically uses Codex when available
- **🔄 Automatic Fallback**: Seamless switching when quotas exhausted
- **📊 Monitoring**: All CLI usage logged in vault/logs/

## 🎉 What You've Gained

1. **Cost Optimization**: Automatically use cheaper/free CLIs when possible
2. **Reliability**: Never get stuck when one CLI fails or hits quota
3. **Performance**: Right CLI for the right task type
4. **Flexibility**: Easy switching between CLIs based on needs
5. **Monitoring**: Full visibility into CLI usage and quotas
6. **Cross-Platform**: Works on Windows, Linux, macOS

Your Personal AI Employee now has **enterprise-grade resilience** with multiple AI providers! 🚀