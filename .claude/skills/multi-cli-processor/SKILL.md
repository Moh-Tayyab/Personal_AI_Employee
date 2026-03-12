# Multi-CLI Processor Skill

**Name:** multi-cli-processor
**Description:** Intelligently route tasks between Claude, Qwen, and Codex CLIs with automatic fallback
**Version:** 1.0.0

## Overview

This skill provides intelligent routing between multiple AI CLIs (Claude, Qwen, Codex) with automatic fallback when quotas are exhausted or CLIs are unavailable.

## Features

- **Automatic CLI Selection**: Routes tasks to the most appropriate CLI based on task type
- **Quota Management**: Tracks API quotas and switches CLIs when limits are reached
- **Fallback System**: Seamlessly falls back to available CLIs when primary fails
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Task-Type Routing**: Different CLIs for different task types (code, reasoning, simple processing)

## Task Routing Logic

| Task Type | Primary CLI | Secondary | Tertiary |
|-----------|-------------|-----------|----------|
| Code Generation | Codex | Claude | Qwen |
| Code Debugging | Codex | Claude | Qwen |
| Complex Reasoning | Claude | Qwen | Codex |
| Planning & Strategy | Claude | Qwen | Codex |
| Simple Processing | Qwen | Claude | Codex |
| Data Extraction | Qwen | Claude | Codex |

## Usage

### Command Line

```bash
# Test all CLIs
python orchestrator.py --test-clis --vault ./vault

# Check quota status
python orchestrator.py --quota-status --vault ./vault

# Force specific CLI
python orchestrator.py --force-cli qwen --vault ./vault

# Use with fallback (default)
python orchestrator.py --primary-cli claude --vault ./vault
```

### Startup Scripts

```bash
# Linux/macOS
./scripts/start_multi_cli.sh --vault ./vault --live --primary-cli claude

# Windows
scripts\start_multi_cli.bat --vault .\vault --live --primary-cli claude
```

### Programmatic Usage

```python
from scripts.multi_cli_manager import MultiCLIManager

# Initialize manager
manager = MultiCLIManager("./vault")

# Process with best available CLI
cli_used, result = manager.process_with_best_cli(
    prompt="Analyze this email and suggest actions",
    context="Email from client about project deadline"
)

print(f"Used {cli_used}: {result}")
```

## Configuration

Edit `vault/config/cli_fallback.yaml`:

```yaml
fallback_strategy:
  primary: "claude"
  secondary: "qwen"
  tertiary: "codex"

quota_limits:
  claude:
    daily_limit: 1000
    warning_threshold: 100
  codex:
    daily_limit: 500
    warning_threshold: 50
```

## CLI Installation

### Claude CLI
Follow the official Claude Code installation guide.

### Qwen CLI
```bash
pip install qwen-cli
```

### GitHub Copilot CLI
```bash
gh extension install github/gh-copilot
```

## Monitoring

### Quota Status
```bash
python scripts/quota_manager.py --status
```

### CLI Health Check
```bash
python scripts/multi_cli_manager.py --test
```

### Logs
Check `vault/logs/cli_manager.log` for detailed activity logs.

## Error Handling

The system handles various error scenarios:

- **Quota Exhausted**: Automatically switches to next available CLI
- **Network Errors**: Retries with exponential backoff
- **CLI Not Found**: Falls back to available CLIs
- **Authentication Errors**: Logs error and tries alternative

## Best Practices

1. **Set Realistic Quotas**: Configure daily limits based on your usage patterns
2. **Monitor Usage**: Regularly check quota status to avoid surprises
3. **Test Regularly**: Use `--test-clis` to ensure all CLIs are working
4. **Keep Fallbacks**: Always have at least 2 CLIs configured
5. **Local Backup**: Qwen can run locally as ultimate fallback

## Troubleshooting

### Common Issues

**"No CLIs available"**
- Install at least one CLI (Claude, Qwen, or Codex)
- Check CLI authentication/setup

**"Quota exhausted"**
- Wait for quota reset (usually daily)
- Use `--reset-quotas` to clear tracking (if quotas actually reset)

**"CLI test failed"**
- Check CLI installation and authentication
- Verify network connectivity
- Check API keys in environment variables

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python orchestrator.py --vault ./vault
```

## Integration with Personal AI Employee

This skill integrates seamlessly with the Personal AI Employee system:

- **Orchestrator**: Automatically uses multi-CLI for all AI processing
- **Watchers**: Email/file processing routes through multi-CLI
- **MCP Servers**: Action execution can use appropriate CLI
- **Approval System**: Complex decisions use Claude, simple ones use Qwen

## Performance Optimization

- **Caching**: Responses cached for 30 minutes for similar prompts
- **Parallel Processing**: Independent tasks processed concurrently
- **Smart Routing**: Task-type analysis for optimal CLI selection
- **Quota Prediction**: Proactive switching before limits hit

## Security Considerations

- API keys stored in environment variables only
- No sensitive data logged
- Quota tracking stored locally only
- CLI responses not cached if they contain sensitive information