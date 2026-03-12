# Playwright CLI + MCP Server Setup ✅

## Installation Complete

### 1. Node.js Check
```bash
node -v
# v24.14.0 ✅ (Required: 18+)
```

### 2. Playwright CLI Install
```bash
npm install -g @playwright/cli@latest
```

### 3. Playwright MCP Server Install
```bash
claude mcp add playwright npx @playwright/mcp@latest
```

### 4. Skill Installation
```bash
mkdir -p .claude/skills/playwright-cli
curl -o .claude/skills/playwright-cli/SKILL.md \
  https://raw.githubusercontent.com/microsoft/playwright-cli/main/skills/playwright-cli/SKILL.md
```

### 5. Permissions Setup
```bash
# Create .claude/settings.json with auto-allow permissions
{
  "permissions": {
    "allow": ["mcp__playwright__*"]
  }
}
```

## Available Commands (40+)

## CLI vs MCP - Key Difference

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Playwright CLI** | Fast browser commands | Direct automation, scripts |
| **Playwright MCP** | AI tool integration | Claude agent control |

**Best Practice:** Use both together for maximum power!

---

## CLI Commands

### Core Commands
| Command | Description |
|---------|-------------|
| `open [url]` | Open browser |
| `goto <url>` | Navigate to URL |
| `type <text>` | Type text |
| `click <ref>` | Click element |
| `fill <ref> <text>` | Fill input field |
| `screenshot` | Take screenshot |
| `snapshot` | Get page snapshot |
| `close` | Close browser |

### Navigation
- `go-back` - Go back
- `go-forward` - Go forward
- `reload` - Reload page

### Storage
- `cookie-list`, `cookie-set`, `cookie-delete`
- `localstorage-list`, `localstorage-set`
- `state-save`, `state-load`

### Advanced
- `route` - Mock network requests
- `tracing-start/stop` - Start/stop tracing
- `video-start/stop` - Record video
- `console` - View console messages

## Usage Examples

### Basic Web Research
```bash
# Claude Code ko bolo:
Use playwright-cli to search Google for "AI agent frameworks 2026".
Open the first result and summarize it.
```

### Form Automation
```bash
playwright-cli open https://example.com/form
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
```

### Screenshot + Report
```bash
# Claude Code ko bolo:
Research top AI startups in Pakistan.
Use playwright-cli to open their websites.
Extract founders and funding.
Create a report.md file.
```

## Project Structure
```
your-project/
├── .claude/
│   └── skills/
│       └── playwright-cli/
│           └── SKILL.md
├── agents/
│   └── web_agent.md
└── package.json
```

## Next Steps

### 1. Install Browsers
```bash
# Chrome installation (automatically done via npx playwright install chrome)
npx playwright install chrome

# Alternative browsers
playwright-cli install-browser chromium
playwright-cli install-browser firefox
```

### 2. Test Run
```bash
playwright-cli open https://google.com --headed
```

### 3. Use with Claude Code
```bash
claude
# Then prompt:
# "Use playwright-cli to research AI startups and create a summary report"
```

## Team Setup (GitHub)

Commit the skill folder:
```bash
git add .claude/skills/playwright-cli/
git commit -m "Add Playwright CLI skill for browser automation"
```

## Recommended Stack

```
Claude Code
   │
   ├── Playwright CLI (Browser Control)
   ├── Serper API (Google Search)
   ├── Firecrawl (Web Scraping)
   └── MCP Servers (External Tools)
```

## Resources
- [Playwright CLI GitHub](https://github.com/microsoft/playwright-cli)
- [Playwright MCP Server](https://www.builder.io/blog/playwright-mcp-server-claude-code)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

## MCP Server Tools

Playwright MCP provides these tools to Claude:

| Tool | Description |
|------|-------------|
| `browser_navigate` | Open URL in browser |
| `browser_click` | Click element |
| `browser_type` | Type text |
| `browser_select_text` | Select dropdown option |
| `browser_hover` | Hover over element |
| `browser_wait` | Wait for condition |
| `browser_screenshot` | Capture screenshot |
| `browser_snapshot` | Get page accessibility snapshot |
| `browser_close` | Close browser |

## Example Prompts for Claude

### Web Research
```
Use Playwright to open https://news.ycombinator.com
Take a screenshot and summarize the top 5 posts.
```

### UI Testing
```
Test my Next.js website locally.
Open localhost:3000
Click all buttons
Find UI bugs
Create a bug report.
```

### Web Scraping
```
Research top AI startups in Pakistan.
Use Playwright to open their websites.
Extract founders and funding.
Create a report.md file.
```

## Ultimate AI Agent Stack

```
Claude Code
   │
   ├── Playwright MCP (Browser Control)
   ├── Playwright CLI (Direct Commands)
   ├── Serper MCP (Google Search)
   ├── Filesystem MCP (File Operations)
   ├── Git MCP (Version Control)
   └── Custom MCPs (Domain Specific)
```

This stack enables:
- ✅ Web browsing
- ✅ Code testing
- ✅ UI automation
- ✅ GitHub commits
- ✅ Autonomous research
